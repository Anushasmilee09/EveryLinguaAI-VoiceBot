// EveryLingua AI - Service Worker
// Advanced PWA functionality with intelligent caching strategies

const CACHE_NAME = 'everylinguaai-v1.2.0';
const STATIC_CACHE_NAME = 'everylinguaai-static-v1.2.0';
const DYNAMIC_CACHE_NAME = 'everylinguaai-dynamic-v1.2.0';
const API_CACHE_NAME = 'everylinguaai-api-v1.2.0';

// Cache strategies configuration
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
  NETWORK_ONLY: 'network-only',
  CACHE_ONLY: 'cache-only'
};

// Resources to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/dealer_dashboard.html',
  '/dealer_locator.html',
  '/register.html',
  '/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// API endpoints to cache with different strategies
const API_CACHE_PATTERNS = [
  { pattern: /\/api\/config/, strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE, maxAge: 3600000 }, // 1 hour
  { pattern: /\/api\/bikes/, strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE, maxAge: 1800000 }, // 30 minutes
  { pattern: /\/api\/services/, strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE, maxAge: 1800000 }, // 30 minutes
  { pattern: /\/api\/dealerships/, strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE, maxAge: 3600000 }, // 1 hour
  { pattern: /\/api\/chat/, strategy: CACHE_STRATEGIES.NETWORK_FIRST, maxAge: 300000 }, // 5 minutes
  { pattern: /\/api\/register/, strategy: CACHE_STRATEGIES.NETWORK_ONLY },
  { pattern: /\/api\/voice-command/, strategy: CACHE_STRATEGIES.NETWORK_FIRST }
];

// Resources that should never be cached
const NETWORK_ONLY_PATTERNS = [
  /\/api\/register\//,
  /\/api\/otp\//,
  /\/api\/ivr\/respond/,
  /\/api\/human-agent\//,
  /\/health/
];

// Maximum cache sizes
const CACHE_LIMITS = {
  [STATIC_CACHE_NAME]: 50,
  [DYNAMIC_CACHE_NAME]: 100,
  [API_CACHE_NAME]: 200
};

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    Promise.all([
      cacheStaticAssets(),
      self.skipWaiting() // Force activation of new service worker
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    Promise.all([
      cleanupOldCaches(),
      self.clients.claim() // Take control of all clients
    ])
  );
});

// Fetch event - handle all network requests
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests for caching
  if (request.method !== 'GET') {
    if (isAPIRequest(url)) {
      event.respondWith(handleAPIRequest(request));
    }
    return;
  }
  
  // Handle different types of requests
  if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
  } else if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isNavigationRequest(request)) {
    event.respondWith(handleNavigationRequest(request));
  } else {
    event.respondWith(handleDynamicRequest(request));
  }
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  switch (event.tag) {
    case 'background-sync-chat':
      event.waitUntil(syncChatMessages());
      break;
    case 'background-sync-registration':
      event.waitUntil(syncRegistrationData());
      break;
    case 'background-sync-bookings':
      event.waitUntil(syncBookingData());
      break;
  }
});

// Push notifications
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New message from EveryLingua AI',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open App',
        icon: '/favicon.ico'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/favicon.ico'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('EveryLingua AI', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handler for communication with main thread
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data);
  
  switch (event.data.type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    case 'CACHE_URLS':
      event.waitUntil(cacheUrls(event.data.payload));
      break;
    case 'CLEAR_CACHE':
      event.waitUntil(clearSpecificCache(event.data.payload));
      break;
    case 'GET_CACHE_SIZE':
      event.waitUntil(getCacheSize().then(size => {
        event.ports[0].postMessage({ type: 'CACHE_SIZE', payload: size });
      }));
      break;
  }
});

// Helper Functions

async function cacheStaticAssets() {
  try {
    const cache = await caches.open(STATIC_CACHE_NAME);
    console.log('[SW] Caching static assets...');
    
    // Cache assets with retry logic
    const cachePromises = STATIC_ASSETS.map(async (asset) => {
      try {
        await cache.add(asset);
        console.log(`[SW] Cached: ${asset}`);
      } catch (error) {
        console.warn(`[SW] Failed to cache ${asset}:`, error);
      }
    });
    
    await Promise.allSettled(cachePromises);
    console.log('[SW] Static assets cached successfully');
  } catch (error) {
    console.error('[SW] Error caching static assets:', error);
  }
}

async function cleanupOldCaches() {
  try {
    const cacheNames = await caches.keys();
    const validCacheNames = [STATIC_CACHE_NAME, DYNAMIC_CACHE_NAME, API_CACHE_NAME];
    
    const deletePromises = cacheNames
      .filter(cacheName => !validCacheNames.includes(cacheName))
      .map(cacheName => {
        console.log(`[SW] Deleting old cache: ${cacheName}`);
        return caches.delete(cacheName);
      });
    
    await Promise.all(deletePromises);
    console.log('[SW] Old caches cleaned up');
  } catch (error) {
    console.error('[SW] Error cleaning up caches:', error);
  }
}

async function handleStaticAsset(request) {
  try {
    // Cache first strategy for static assets
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Error handling static asset:', error);
    return caches.match('/offline.html') || new Response('Asset not available offline');
  }
}

async function handleAPIRequest(request) {
  const url = new URL(request.url);
  
  // Check if this endpoint should never be cached
  if (NETWORK_ONLY_PATTERNS.some(pattern => pattern.test(url.pathname))) {
    return handleNetworkOnly(request);
  }
  
  // Find matching cache pattern
  const cachePattern = API_CACHE_PATTERNS.find(pattern => 
    pattern.pattern.test(url.pathname)
  );
  
  if (!cachePattern) {
    return handleNetworkFirst(request, API_CACHE_NAME);
  }
  
  switch (cachePattern.strategy) {
    case CACHE_STRATEGIES.CACHE_FIRST:
      return handleCacheFirst(request, API_CACHE_NAME, cachePattern.maxAge);
    case CACHE_STRATEGIES.NETWORK_FIRST:
      return handleNetworkFirst(request, API_CACHE_NAME, cachePattern.maxAge);
    case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
      return handleStaleWhileRevalidate(request, API_CACHE_NAME, cachePattern.maxAge);
    case CACHE_STRATEGIES.NETWORK_ONLY:
      return handleNetworkOnly(request);
    case CACHE_STRATEGIES.CACHE_ONLY:
      return handleCacheOnly(request, API_CACHE_NAME);
    default:
      return handleNetworkFirst(request, API_CACHE_NAME);
  }
}

async function handleNavigationRequest(request) {
  try {
    // Network first for navigation requests
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed for navigation, trying cache...');
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fallback to main page for SPA routing
    return caches.match('/') || new Response('App not available offline');
  }
}

async function handleDynamicRequest(request) {
  return handleStaleWhileRevalidate(request, DYNAMIC_CACHE_NAME);
}

async function handleCacheFirst(request, cacheName, maxAge) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse && !isExpired(cachedResponse, maxAge)) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      const responseWithTimestamp = addTimestamp(networkResponse.clone());
      cache.put(request, responseWithTimestamp);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache first failed:', error);
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response('Resource not available');
  }
}

async function handleNetworkFirst(request, cacheName, maxAge) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      const responseWithTimestamp = addTimestamp(networkResponse.clone());
      cache.put(request, responseWithTimestamp);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache...');
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse && !isExpired(cachedResponse, maxAge)) {
      return cachedResponse;
    }
    
    throw error;
  }
}

async function handleStaleWhileRevalidate(request, cacheName, maxAge) {
  const cachedResponse = await caches.match(request);
  
  // Return cached response immediately if available
  const responsePromise = cachedResponse && !isExpired(cachedResponse, maxAge)
    ? Promise.resolve(cachedResponse)
    : fetch(request).then(async networkResponse => {
        if (networkResponse.ok) {
          const cache = await caches.open(cacheName);
          const responseWithTimestamp = addTimestamp(networkResponse.clone());
          cache.put(request, responseWithTimestamp);
        }
        return networkResponse;
      }).catch(() => cachedResponse || new Response('Resource not available'));
  
  // Update cache in background if we have a cached response
  if (cachedResponse) {
    fetch(request).then(async networkResponse => {
      if (networkResponse.ok) {
        const cache = await caches.open(cacheName);
        const responseWithTimestamp = addTimestamp(networkResponse.clone());
        cache.put(request, responseWithTimestamp);
      }
    }).catch(() => {}); // Ignore background update failures
  }
  
  return responsePromise;
}

async function handleNetworkOnly(request) {
  return fetch(request);
}

async function handleCacheOnly(request, cacheName) {
  return caches.match(request) || new Response('Resource not available offline');
}

// Utility functions

function isStaticAsset(url) {
  return STATIC_ASSETS.some(asset => {
    if (typeof asset === 'string') {
      return url.href.includes(asset) || url.pathname === asset;
    }
    return false;
  }) || /\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|ico)$/i.test(url.pathname);
}

function isAPIRequest(url) {
  return url.pathname.startsWith('/api/');
}

function isNavigationRequest(request) {
  return request.mode === 'navigate' || 
         (request.method === 'GET' && request.headers.get('accept').includes('text/html'));
}

function addTimestamp(response) {
  const headers = new Headers(response.headers);
  headers.set('sw-cached-at', Date.now().toString());
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

function isExpired(response, maxAge) {
  if (!maxAge) return false;
  
  const cachedAt = response.headers.get('sw-cached-at');
  if (!cachedAt) return false;
  
  return Date.now() - parseInt(cachedAt) > maxAge;
}

async function cacheUrls(urls) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    await Promise.allSettled(urls.map(url => cache.add(url)));
    console.log('[SW] URLs cached successfully');
  } catch (error) {
    console.error('[SW] Error caching URLs:', error);
  }
}

async function clearSpecificCache(cacheName) {
  try {
    const deleted = await caches.delete(cacheName);
    console.log(`[SW] Cache ${cacheName} cleared:`, deleted);
    return deleted;
  } catch (error) {
    console.error('[SW] Error clearing cache:', error);
    return false;
  }
}

async function getCacheSize() {
  try {
    const cacheNames = await caches.keys();
    const sizes = {};
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const keys = await cache.keys();
      sizes[cacheName] = keys.length;
    }
    
    return sizes;
  } catch (error) {
    console.error('[SW] Error getting cache size:', error);
    return {};
  }
}

// Background sync functions

async function syncChatMessages() {
  try {
    console.log('[SW] Syncing chat messages...');
    // Implementation for syncing offline chat messages
    // This would typically retrieve stored messages from IndexedDB
    // and send them to the server when online
    
    // Placeholder implementation
    const messages = await getStoredChatMessages();
    for (const message of messages) {
      try {
        await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(message)
        });
        await removeStoredChatMessage(message.id);
      } catch (error) {
        console.error('[SW] Failed to sync message:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Error syncing chat messages:', error);
  }
}

async function syncRegistrationData() {
  try {
    console.log('[SW] Syncing registration data...');
    // Implementation for syncing offline registration attempts
    const registrations = await getStoredRegistrations();
    
    for (const registration of registrations) {
      try {
        await fetch('/api/register/send-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(registration)
        });
        await removeStoredRegistration(registration.id);
      } catch (error) {
        console.error('[SW] Failed to sync registration:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Error syncing registration data:', error);
  }
}

async function syncBookingData() {
  try {
    console.log('[SW] Syncing booking data...');
    // Implementation for syncing offline booking attempts
    const bookings = await getStoredBookings();
    
    for (const booking of bookings) {
      try {
        const endpoint = booking.type === 'test-ride' 
          ? '/api/test-ride-booking' 
          : '/api/service-booking';
          
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(booking.data)
        });
        await removeStoredBooking(booking.id);
      } catch (error) {
        console.error('[SW] Failed to sync booking:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Error syncing booking data:', error);
  }
}

// Placeholder functions for IndexedDB operations
// In a real implementation, these would interact with IndexedDB

async function getStoredChatMessages() {
  // Return stored chat messages from IndexedDB
  return [];
}

async function removeStoredChatMessage(id) {
  // Remove synced message from IndexedDB
}

async function getStoredRegistrations() {
  // Return stored registrations from IndexedDB
  return [];
}

async function removeStoredRegistration(id) {
  // Remove synced registration from IndexedDB
}

async function getStoredBookings() {
  // Return stored bookings from IndexedDB
  return [];
}

async function removeStoredBooking(id) {
  // Remove synced booking from IndexedDB
}

// Cache size management
async function manageCacheSize() {
  try {
    for (const [cacheName, limit] of Object.entries(CACHE_LIMITS)) {
      const cache = await caches.open(cacheName);
      const keys = await cache.keys();
      
      if (keys.length > limit) {
        // Remove oldest entries
        const toRemove = keys.slice(0, keys.length - limit);
        await Promise.all(toRemove.map(key => cache.delete(key)));
        console.log(`[SW] Cleaned ${toRemove.length} entries from ${cacheName}`);
      }
    }
  } catch (error) {
    console.error('[SW] Error managing cache size:', error);
  }
}

// Periodic cache cleanup
setInterval(manageCacheSize, 3600000); // Run every hour

console.log('[SW] Service worker script loaded successfully');