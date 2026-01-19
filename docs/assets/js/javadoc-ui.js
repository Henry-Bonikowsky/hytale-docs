// Hytale Plugin Documentation - UI Interactions

document.addEventListener('DOMContentLoaded', function() {

  // Package collapse/expand functionality
  document.querySelectorAll('.package-name[data-toggle="collapse"]').forEach(function(packageName) {
    const packageSection = packageName.closest('.package-section');
    const packageClasses = packageSection.querySelector('.package-classes');

    // Set initial max-height for animation
    if (packageClasses) {
      packageClasses.style.maxHeight = packageClasses.scrollHeight + 'px';
    }

    packageName.addEventListener('click', function() {
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
    const originalContent = sidebarNav.innerHTML;

    // Load search index
    fetch('../assets/search-index.json')
      .then(response => response.json())
      .then(data => {
        searchIndex = data;
      })
      .catch(err => console.error('Failed to load search index:', err));

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim();

      clearTimeout(searchTimeout);

      if (query.length < 1) {
        // Restore original sidebar content
        sidebarNav.innerHTML = originalContent;
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
                return `<a href="${entry.file}" class="class-link" style="display: block; color: #A3B50B; text-decoration: none; padding: 0.375rem 0.75rem; margin: 0.125rem 0; border-radius: 0.25rem; transition: all 0.15s; font-family: 'Courier New', monospace;">${entry.name}</a>`;
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
