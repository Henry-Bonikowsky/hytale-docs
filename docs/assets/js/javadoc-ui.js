// Hytale Plugin Documentation - UI Interactions

// Extract collapse setup into reusable function
function setupCollapseHandlers() {
  document.querySelectorAll('.package-name[data-toggle="collapse"]').forEach(function(packageName) {
    const packageSection = packageName.closest('.package-section');
    const packageClasses = packageSection.querySelector('.package-classes');

    // Set initial max-height for animation
    if (packageClasses) {
      packageClasses.style.maxHeight = packageClasses.scrollHeight + 'px';
    }

    // Remove old listener if exists (to prevent duplicates)
    const newPackageName = packageName.cloneNode(true);
    packageName.parentNode.replaceChild(newPackageName, packageName);

    newPackageName.addEventListener('click', function() {
      const isCollapsed = packageSection.classList.contains('collapsed');

      if (isCollapsed) {
        // Expand
        packageSection.classList.remove('collapsed');
        packageClasses.style.maxHeight = packageClasses.scrollHeight + 'px';
      } else {
        // Collapse
        packageSection.classList.add('collapsed');
        packageClasses.style.maxHeight = '0';
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {

  // Package collapse/expand functionality
  setupCollapseHandlers();

  // Toggle private/protected members visibility
  const visibilityToggle = document.getElementById('show-private');
  if (visibilityToggle) {
    visibilityToggle.addEventListener('change', function() {
      const privateMembers = document.querySelectorAll('.private-member, .protected-member');
      privateMembers.forEach(function(member) {
        if (visibilityToggle.checked) {
          member.style.display = '';
        } else {
          member.style.display = 'none';
        }
      });

      // Update URL hash
      if (visibilityToggle.checked) {
        window.location.hash = 'show-private';
      } else {
        window.location.hash = '';
      }
    });

    // Check initial state from URL hash
    if (window.location.hash === '#show-private') {
      visibilityToggle.checked = true;
    } else {
      // Hide private members by default
      const privateMembers = document.querySelectorAll('.private-member, .protected-member');
      privateMembers.forEach(function(member) {
        member.style.display = 'none';
      });
    }
  }

  // Global search with sidebar replacement
  const searchInput = document.querySelector('.sidebar-search input');
  const sidebarNav = document.querySelector('.sidebar-nav');

  if (searchInput && sidebarNav) {
    let searchIndex = [];
    let searchTimeout = null;
    let originalContent = null;

    // Load search index
    fetch('../assets/search-index.json')
      .then(response => response.json())
      .then(data => {
        searchIndex = data;

        // Populate sidebar with nearby classes (same package as current class)
        populateNearbyClasses();

        // Save original content AFTER populating
        setTimeout(() => {
          originalContent = sidebarNav.innerHTML;
        }, 200);
      })
      .catch(err => console.error('Failed to load search index:', err));

    function populateNearbyClasses() {
      // Get current class name from page title
      const pageTitle = document.title.split(' - ')[0];

      if (!pageTitle || pageTitle === 'Hytale API - All Classes') return;

      // Find current class in search index
      const currentClass = searchIndex.find(entry => entry.type === 'class' && entry.name === pageTitle);

      if (!currentClass || !currentClass.package) return;

      // Find all classes in the same package
      const nearbyClasses = searchIndex.filter(entry => {
        if (entry.type !== 'class') return false;
        if (entry.name === pageTitle) return false;
        return entry.package === currentClass.package;
      });

      // Sort alphabetically
      nearbyClasses.sort((a, b) => a.name.localeCompare(b.name));

      // Replace sidebar content with nearby classes
      // Shorten package name to last 2-3 segments
      let packageDisplay = currentClass.package || 'Default Package';
      const packageParts = packageDisplay.split('.');
      if (packageParts.length > 3) {
        // Show last 3 segments (e.g., "universe.world.events" instead of "com.hypixel.hytale.server.core.universe.world.events")
        packageDisplay = '...' + packageParts.slice(-3).join('.');
      }

      sidebarNav.innerHTML = `
        <div class="package-group">
          <div class="package-title" title="${currentClass.package}">${packageDisplay}</div>
          <div style="margin-top: 1rem;">
            <a href="${currentClass.file}" class="class-link active">${currentClass.name}</a>
            ${nearbyClasses.map(entry => {
              return `<a href="${entry.file}" class="class-link">${entry.name}</a>`;
            }).join('')}
          </div>
        </div>
      `;
    }

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim();

      clearTimeout(searchTimeout);

      if (query.length < 1) {
        // Restore original sidebar content
        if (originalContent) {
          sidebarNav.innerHTML = originalContent;
          // Re-setup collapse functionality after restore
          setupCollapseHandlers();
        }
        return;
      }

      searchTimeout = setTimeout(() => {
        const lowerQuery = query.toLowerCase();
        const results = [];

        // Search for classes only (not methods)
        for (const entry of searchIndex) {
          if (entry.type === 'class') {
            const lowerName = entry.name.toLowerCase();
            if (lowerName.includes(lowerQuery)) {
              results.push(entry);
              if (results.length >= 20) break;
            }
          }
        }

        if (results.length === 0) {
          sidebarNav.innerHTML = '<div style="color: #6c717d; text-align: center; padding: 2rem;">No classes found</div>';
          return;
        }

        // Replace sidebar content with search results
        sidebarNav.innerHTML = `
          <div class="package-group">
            <div class="package-title">Search Results (${results.length})</div>
            <div style="margin-top: 1rem;">
              ${results.map(entry => {
                return `<a href="${entry.file}" class="class-link">${entry.name}</a>`;
              }).join('')}
            </div>
          </div>
        `;
      }, 150);
    });
  }

  // Add tooltip for type links (show full qualified name)
  document.querySelectorAll('.type-link').forEach(function(link) {
    const fullName = link.getAttribute('data-full-name');
    if (fullName) {
      link.setAttribute('title', fullName);

      // Initialize Bootstrap tooltips if available
      if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        new bootstrap.Tooltip(link);
      }
    }
  });

});
