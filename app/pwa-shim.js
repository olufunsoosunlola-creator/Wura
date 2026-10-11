// WURA home-screen app shim. Loaded before support.js / image-slot.js.
(function () {
  // 1. Serve React from this site instead of unpkg, so the app opens offline.
  //    support.js still checks the same SRI hashes against these files.
  window.__resources = {
    'https://unpkg.com/react@18.3.1/umd/react.production.min.js': 'vendor/react.production.min.js',
    'https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js': 'vendor/react-dom.production.min.js'
  };

  // 2. Let <image-slot> keep the paintings you drop in, on this device.
  //    image-slot.js reads '.image-slots.state.json' with fetch() and writes
  //    through window.omelette.writeFile; both are routed to IndexedDB here.
  var SIDECAR = '.image-slots.state.json';
  var SHIPPED = 'image-slots.state.json';
  var dbP = null;
  function db() {
    if (dbP) return dbP;
    dbP = new Promise(function (res, rej) {
      var r = indexedDB.open('wura-files', 1);
      r.onupgradeneeded = function () { r.result.createObjectStore('files'); };
      r.onsuccess = function () { res(r.result); };
      r.onerror = function () { rej(r.error); };
    });
    return dbP;
  }
  function idb(mode, fn) {
    return db().then(function (d) {
      return new Promise(function (res, rej) {
        var tx = d.transaction('files', mode);
        var req = fn(tx.objectStore('files'));
        tx.oncomplete = function () { res(req && req.result); };
        tx.onerror = function () { rej(tx.error); };
      });
    });
  }
  window.omelette = window.omelette || {};
  window.omelette.writeFile = function (name, content) {
    return idb('readwrite', function (s) { return s.put(content, name); });
  };
  var realFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    var path = url.split('?')[0].split('#')[0].replace(location.origin, '').replace(/^.*\//, '');
    if (path === SIDECAR) {
      return idb('readonly', function (s) { return s.get(SIDECAR); })
        .catch(function () { return null; })
        .then(function (local) {
          if (typeof local === 'string') return new Response(local, { headers: { 'Content-Type': 'application/json' } });
          return realFetch(SHIPPED, init);
        });
    }
    return realFetch(input, init);
  };

  // 3. Offline + install support.
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }
})();
