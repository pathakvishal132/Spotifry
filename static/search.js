
  // Function to handle search and highlight functionality
  function searchAndHighlight() {
    // Get the value typed in the search input
    var searchTerm = $('input[name="search"]').val();

    // Remove any previous highlights
    $('.highlight').removeClass('highlight');

    // Highlight the search term in the categories and products
    $('.card-header h5').each(function () {
      var text = $(this).text();
      var highlightedText = text.replace(new RegExp(searchTerm, 'gi'), '<span class="highlight">' + searchTerm + '</span>');
      $(this).html(highlightedText);
    });

    $('.card-title').each(function () {
      var text = $(this).text();
      var highlightedText = text.replace(new RegExp(searchTerm, 'gi'), '<span class="highlight">' + searchTerm + '</span>');
      $(this).html(highlightedText);
    });
  }

  // Attach the searchAndHighlight function to the search form submission
  $(document).on('submit', 'form[role="search"]', function (event) {
    event.preventDefault(); // Prevent the form from submitting
    searchAndHighlight(); // Call the searchAndHighlight function
  });
