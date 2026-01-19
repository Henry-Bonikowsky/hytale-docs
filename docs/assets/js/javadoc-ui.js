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

  // Global search with autocomplete
  const searchInput = document.querySelector('.sidebar-search input');
  if (searchInput) {
    let searchIndex = [];
    let searchTimeout = null;

    // Load search index
    fetch('../assets/search-index.json')
      .then(response => response.json())
      .then(data => {
        searchIndex = data;
      })
      .catch(err => console.error('Failed to load search index:', err));

    // Create dropdown for results
    const dropdown = document.createElement('div');
    dropdown.style.cssText = 'position: absolute; top: 100%; left: 0; right: 0; background: #252b3d; border: 2px solid #A3B50B; border-top: none; border-radius: 0 0 6px 6px; max-height: 300px; overflow-y: auto; z-index: 1000; display: none;';
    searchInput.parentElement.style.position = 'relative';
    searchInput.parentElement.appendChild(dropdown);

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim();

      clearTimeout(searchTimeout);

      if (query.length < 1) {
        dropdown.style.display = 'none';
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
              if (results.length >= 10) break;
            }
          }
        }

        if (results.length === 0) {
          dropdown.style.display = 'none';
          return;
        }

        dropdown.innerHTML = results.map(entry => {
          return `<a href="${entry.file}" style="display: block; color: #A3B50B; text-decoration: none; padding: 8px 12px; border-bottom: 1px solid #2d3548; font-family: 'Courier New', monospace; transition: background 0.1s;" onmouseover="this.style.background='#2d3548'" onmouseout="this.style.background='transparent'">${entry.name}</a>`;
        }).join('');

        dropdown.style.display = 'block';
      }, 150);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
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
