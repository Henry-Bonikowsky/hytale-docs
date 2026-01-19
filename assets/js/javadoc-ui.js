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

  // Simple search filtering for sidebar
  const searchInput = document.querySelector('.sidebar-search input');
  if (searchInput) {
    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.toLowerCase();
      const packageSections = document.querySelectorAll('.package-section');

      packageSections.forEach(function(section) {
        const classLinks = section.querySelectorAll('.class-link');
        let hasVisibleLinks = false;

        classLinks.forEach(function(link) {
          const text = link.textContent.toLowerCase();

          if (text.includes(query) || query === '') {
            link.style.display = '';
            hasVisibleLinks = true;
          } else {
            link.style.display = 'none';
          }
        });

        // Hide entire package section if no visible links
        if (!hasVisibleLinks) {
          section.style.display = 'none';
        } else {
          section.style.display = '';
          // Auto-expand if searching and has results
          if (query !== '') {
            section.classList.remove('collapsed');
            const packageClasses = section.querySelector('.package-classes');
            if (packageClasses) {
              packageClasses.style.maxHeight = packageClasses.scrollHeight + 'px';
            }
          }
        }
      });
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
