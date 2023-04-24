// Search bar
const searchInput = document.querySelector('#search-input');
const tableRows = document.querySelectorAll('tbody tr');

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

// Score colors
function highlightMaxValues() {
    const rows = document.querySelectorAll('tbody tr');

    rows.forEach(row => {
      let maxLocal = 0;
      let maxVisitor = 0;
      let minLocal = Infinity;
      let minVisitor = Infinity;
      let cellsLocal = row.querySelectorAll('.local');
      let cellsVisitor = row.querySelectorAll('.visitor');
      let cellsResult = row.querySelectorAll('.result');
  
      cellsLocal.forEach(cell => {
        const value = parseInt(cell.textContent);
        if (value > maxLocal) {
          maxLocal = value;
        }
        if (value < minLocal) {
          minLocal = value;
        }
      });
  
      cellsVisitor.forEach(cell => {
        const value = parseInt(cell.textContent);
        if (value > maxVisitor) {
          maxVisitor = value;
        }
        if (value < minVisitor) {
          minVisitor = value;
        }
      });
  
      cellsLocal.forEach(cell => {
        const value = parseInt(cell.textContent);
        if (value === maxLocal && value > minVisitor) {
          cell.classList.add('highlight');
        } else if (value === minLocal && value < maxVisitor) {
          cell.classList.add('lowlight');
        } else {
          cell.classList.remove('highlight');
          cell.classList.remove('lowlight');
        }
      });
  
      cellsVisitor.forEach(cell => {
        const value = parseInt(cell.textContent);
        if (value === maxVisitor && value > minLocal) {
          cell.classList.add('highlight');
        } else if (value === minVisitor && value < maxLocal) {
          cell.classList.add('lowlight');
        } else {
          cell.classList.remove('highlight');
          cell.classList.remove('lowlight');
        }
      });

      cellsResult.forEach(cell => {
        const value = cell.textContent.toLowerCase();
        if (value === 'l') {
            cell.classList.add('highlight');
        }
        else if(value === 'v') {
            cell.classList.add('lowlight');
        }
        else {
            cell.classList.remove('highlight');
            cell.classList.remove('lowlight');
        }
    });

    });

  }
