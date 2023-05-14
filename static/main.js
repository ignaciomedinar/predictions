// Search bar
const searchInput = document.querySelector('#search-input');
const tableRows = document.querySelectorAll('tbody tr');

if (searchInput){
searchInput.addEventListener('input', function(event) {
  const inputValue = event.target.value.toLowerCase();
  tableRows.forEach(function(row) {
    const rowText = row.textContent.toLowerCase();
    if (rowText.includes(inputValue)) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
});
}
// // Score colors
// function highlightMaxValues() {
//     const rows = document.querySelectorAll('tbody tr');

//     rows.forEach(row => {
//       let maxLocal = 0;
//       let maxVisitor = 0;
//       let minLocal = Infinity;
//       let minVisitor = Infinity;
//       let cellsLocal = row.querySelectorAll('.local');
//       let cellsVisitor = row.querySelectorAll('.visitor');
//       let cellsResult = row.querySelectorAll('.result');
  
//       cellsLocal.forEach(cell => {
//         const value = parseInt(cell.textContent);
//         if (value > maxLocal) {
//           maxLocal = value;
//         }
//         if (value < minLocal) {
//           minLocal = value;
//         }
//       });
  
//       cellsVisitor.forEach(cell => {
//         const value = parseInt(cell.textContent);
//         if (value > maxVisitor) {
//           maxVisitor = value;
//         }
//         if (value < minVisitor) {
//           minVisitor = value;
//         }
//       });
  
//       cellsLocal.forEach(cell => {
//         const value = parseInt(cell.textContent);
//         if (value === maxLocal && value > minVisitor) {
//           cell.classList.add('highlight');
//         } else if (value === minLocal && value < maxVisitor) {
//           cell.classList.add('lowlight');
//         } else {
//           cell.classList.remove('highlight');
//           cell.classList.remove('lowlight');
//         }
//       });
  
//       cellsVisitor.forEach(cell => {
//         const value = parseInt(cell.textContent);
//         if (value === maxVisitor && value > minLocal) {
//           cell.classList.add('highlight');
//         } else if (value === minVisitor && value < maxLocal) {
//           cell.classList.add('lowlight');
//         } else {
//           cell.classList.remove('highlight');
//           cell.classList.remove('lowlight');
//         }
//       });

//       cellsResult.forEach(cell => {
//         const value = cell.textContent.toLowerCase();
//         if (value === 'l') {
//             cell.classList.add('highlight');
//         }
//         else if(value === 'v') {
//             cell.classList.add('lowlight');
//         }
//         else {
//             cell.classList.remove('highlight');
//             cell.classList.remove('lowlight');
//         }
//     });

//     });

//   }


// //This code is for the dropdown filters in the tables and sorting

$(document).ready(function() {
  // Create an array to hold the distinct values for each column
  var distinctValues = [];

  // Loop through each column header
  $('th').each(function(colIndex) {
    // Create an empty array for this column's distinct values
    distinctValues[colIndex] = [];

    // Loop through each row in the table
    $('tbody tr').each(function(rowIndex) {
      if (rowIndex > 0) {
        var cellValue = $(this).children('td').eq(colIndex).text();

        // Add the cell value to the array if it hasn't been added already
        if ($.inArray(cellValue, distinctValues[colIndex]) === -1) {
          distinctValues[colIndex].push(cellValue);
        }
      }
    });

    // Sort the distinct values alphabetically
    distinctValues[colIndex].sort();

    // Add the distinct values to the corresponding select element
    var select = $('.filter-header[data-col-index="' + colIndex + '"]');
    select.empty(); // clear the select element
    select.append('<option value="">All</option>');
    $.each(distinctValues[colIndex], function(i, value) {
      select.append('<option value="' + value + '">' + value + '</option>');
    });

    // Add change event listener to the select element for filtering
    select.change(function() {
      var colIndex = $(this).data('col-index');
      var selectedValue = $(this).val();
      var tableRows = $('tbody tr');

      // Hide all rows that don't match the selected value
      tableRows.each(function() {
        var cellValue = $(this).children('td').eq(colIndex).text();
        if (selectedValue === "" || cellValue === selectedValue) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });

      // Update the other select elements to only show available options
      $('.filter-header').each(function() {
        if ($(this).data('col-index') !== colIndex) {
          $(this).find('option').prop('disabled', false);
          tableRows.filter(':visible').each(function() {
            var cellValue = $(this).children('td').eq($(this).find('.filter-header').data('col-index')).text();
            $(this).find('.filter-header option[value="' + cellValue + '"]').prop('disabled', true);
          });
        }
      });
    });

    // Add click event listener to the column header for sorting
    $(this).on('click', function() {
      var rows = $('tbody tr').toArray();

      // Determine the sort direction based on the current state of the column
      var sortDirection = $(this).hasClass('asc') ? -1 : 1;

      // Set the sort direction for the next click
      $(this).toggleClass('asc', sortDirection === 1);
      $(this).toggleClass('desc', sortDirection === -1);

      // Get the index of the column being sorted
      var colIndex = $(this).index();

      // Sort the rows based on the column values
      rows.sort(function(a, b) {
        var aVal = $(a).children('td').eq(colIndex).text();
        var bVal = $(b).children('td').eq(colIndex).text();
        return aVal.localeCompare(bVal) * sortDirection;
      });

      // Rebuild the table with the sorted rows
      $('tbody').html(rows);
    });
  });
});

/*code to check/uncheck all*/

$(document).ready(function() {
    $('#check-all').click(function() {
        $('input[type=checkbox]').prop('checked', $(this).prop('checked'));
    });
});