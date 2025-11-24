//admin
// Get all sidebar links and page sections
const sidebarLinks = document.querySelectorAll('.sidebar ul li a');
const pageSections = document.querySelectorAll('.page-section');

// Add click event to each sidebar link
sidebarLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Remove active class from all links
    sidebarLinks.forEach(l => l.classList.remove('active'));
    
    // Add active class to clicked link
    this.classList.add('active');
    
    // Get the target section id from href
    const targetId = this.getAttribute('href').substring(1);
    
    // Hide all sections
    pageSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the target section
    document.getElementById(targetId).classList.add('active');
  });
});

//patient
// Get all sidebar links and page sections
// const sidebarLinks = document.querySelectorAll('.sidebar ul li a');
// const pageSections = document.querySelectorAll('.page-section');

// Add click event to each sidebar link
sidebarLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Remove active class from all links
    sidebarLinks.forEach(l => l.classList.remove('active'));
    
    // Add active class to clicked link
    this.classList.add('active');
    
    // Get the target section id from href
    const targetId = this.getAttribute('href').substring(1);
    
    // Hide all sections
    pageSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the target section
    document.getElementById(targetId).classList.add('active');
  });
});