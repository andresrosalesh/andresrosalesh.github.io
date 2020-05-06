
window.onload = function () {

    // Fills in table logs with timing and well being data

    // Timings
    let tableRefTiming = document.getElementById('timings-table').getElementsByTagName('tbody')[0];
    // Fill in rows
    for (let i = 0; i < 10; i++) {
        let newRow  = tableRefTiming.insertRow();

        // Fill in columns
        for (let j = 0; j < 5; j++) {
            let newCell  = newRow.insertCell(j);
            newCell.appendChild(document.createTextNode(timings[i][j]));
        }
    }

    // Shutdowns
    let tableRefShutdown = document.getElementById('shutdowns-table').getElementsByTagName('tbody')[0];
    // Fill in rows
    for (let i = 0; i < wbdata.length; i++) {
        let newRow  = tableRefShutdown.insertRow();

        // Fill in columns
        for (let j = 0; j < 6; j++) {
            let newCell  = newRow.insertCell(j);
            newCell.appendChild(document.createTextNode(wbdata[i][j]));
        }
    }
}