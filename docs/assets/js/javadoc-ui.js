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

      // Build package tree with related packages
      const currentPackage = currentClass.package;
      const packageParts = currentPackage.split('.');

      // Get parent package and sibling packages
      const relatedPackages = new Set();

      // Add current package
      relatedPackages.add(currentPackage);

      // Add sibling packages (same parent)
      if (packageParts.length > 1) {
        const parentPackage = packageParts.slice(0, -1).join('.');
        searchIndex.forEach(entry => {
          if (entry.type === 'class' && entry.package && entry.package.startsWith(parentPackage + '.')) {
            const pkgParts = entry.package.split('.');
            if (pkgParts.length === packageParts.length) {
              relatedPackages.add(entry.package);
            }
          }
        });
      }

      // Add child packages (direct children only)
      searchIndex.forEach(entry => {
        if (entry.type === 'class' && entry.package && entry.package.startsWith(currentPackage + '.')) {
          const pkgParts = entry.package.split('.');
          if (pkgParts.length === packageParts.length + 1) {
            relatedPackages.add(entry.package);
          }
        }
      });

      // Build package tree
      const packageTree = {};
      relatedPackages.forEach(pkg => {
        const classes = searchIndex.filter(entry => entry.type === 'class' && entry.package === pkg);
        if (classes.length > 0) {
          packageTree[pkg] = classes.sort((a, b) => a.name.localeCompare(b.name));
        }
      });

      // Fix file paths - extract just the filename from the full path
      const getCurrentFileName = (file) => file.split('/').pop();

      // Render collapsible package tree
      const packages = Object.keys(packageTree).sort();
      sidebarNav.innerHTML = packages.map(pkg => {
        const classes = packageTree[pkg];
        const isCurrentPackage = pkg === currentPackage;

        // Shorten package name for display
        let packageDisplay = pkg;
        const pkgParts = pkg.split('.');
        if (pkgParts.length > 3) {
          packageDisplay = '...' + pkgParts.slice(-3).join('.');
        }

        const classesHtml = classes.map(entry => {
          const isActive = entry.name === pageTitle;
          return `<a href="${getCurrentFileName(entry.file)}" class="class-link ${isActive ? 'active' : ''}">${entry.name}</a>`;
        }).join('');

        return `
          <div class="package-section ${isCurrentPackage ? '' : 'collapsed'}">
            <div class="package-name" data-toggle="collapse" title="${pkg}">
              <span class="chevron">▼</span>
              ${packageDisplay} (${classes.length})
            </div>
            <div class="package-classes" style="max-height: ${isCurrentPackage ? classes.length * 40 : 0}px;">
              ${classesHtml}
            </div>
          </div>
        `;
      }).join('');

      // Re-setup collapse handlers for the new content
      setupCollapseHandlers();
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
        const getFileName = (file) => file.split('/').pop();

        sidebarNav.innerHTML = `
          <div class="package-group">
            <div class="package-title">Search Results (${results.length})</div>
            <div style="margin-top: 1rem;">
              ${results.map(entry => {
                return `<a href="${getFileName(entry.file)}" class="class-link">${entry.name}</a>`;
              }).join('')}
            </div>
          </div>
        `;
      }, 150);
    });
  }

  // Make breadcrumb navigation functional
  const breadcrumb = document.querySelector('.navbar-breadcrumb');
  if (breadcrumb) {
    const breadcrumbLinks = breadcrumb.querySelectorAll('a');
    breadcrumbLinks.forEach((link, index) => {
      // Build cumulative package path up to this link
      const packageParts = [];
      for (let i = 0; i <= index; i++) {
        packageParts.push(breadcrumbLinks[i].textContent.trim());
      }
      const packagePath = packageParts.join('.');

      // Update link to go to class browser filtered by this package
      link.href = `index.html?package=${encodeURIComponent(packagePath)}`;
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
