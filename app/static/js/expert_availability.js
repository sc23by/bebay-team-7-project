document.addEventListener("DOMContentLoaded", function () {

    console.log(filledTimeslots);

    const timeSlots = [
            "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
            "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
            "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00"
    ];

    //Works out the dates of the current week to display on the header rows of the availability table.

    const today = new Date();
    const weekDay = today.getDay();
    const currentDay = today.getDate();

    weekdays = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
    weekdaysCapitalised = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

    /*
    Converts a Javascript Date object into a formatted dd/mm/yy string so it can be displayed.

    Parameters:
    var (date): The Javascript date

    Returns:
    str: The dd/mm/yy string
    */

    function formatDate(date){

        const day = String(date.getDate()).padStart(2, '0'); 
        const month = String(date.getMonth() + 1).padStart(2, '0'); 
        const year = String(date.getFullYear()).slice(-2);         
        return `${day}/${month}/${year}`;
        }

    for(day=0;day<7;day++){
    let currentDate = new Date(today)
    currentDate.setDate(today.getDate() - weekDay + day)
    document.getElementById(weekdays[day]+'-date').textContent = `${weekdaysCapitalised[day]} ${formatDate(currentDate)}`;
    }

    const tableBody = document.querySelector("#availability-table tbody");
    tableBody.innerHTML = ""; 

    for (let i = 0; i < timeSlots.length; i++) {
        let row = document.createElement("tr");

        let timeSlotCell = document.createElement("td");
        timeSlotCell.textContent = timeSlots[i]; 
        row.appendChild(timeSlotCell);

        for (let j = 0; j < 7; j++) {
            let cell = document.createElement("td");
            cell.dataset.row = i;
            cell.dataset.col = j;

            cell.dataset.startTime = timeSlots[i].split('-')[0];

            let currentDate = new Date(today);
            currentDate.setDate(today.getDate() - weekDay + j);
            const formattedDate = currentDate.toISOString().split("T")[0];
            cell.dataset.date = formattedDate;

            if (filledTimeslots.some(slot => slot.date === formattedDate && slot.start_time === cell.dataset.startTime)) {
            cell.classList.add("filled");
            }

            cell.addEventListener("click", () => cell.classList.toggle("filled"));
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    }
    
    function saveState() {
        const form = document.getElementById("availabilityForm");
        const filledCells = document.querySelectorAll('#availability-table td.filled');
        const baseDate = new Date();  
        const weekDay = today.getDay();  

        let selectedTimeslots = [];

        const timeSlots = [
            "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
            "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
            "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00"
        ];
        
        filledCells.forEach(cell => {
            const rowIndex = cell.dataset.row;  
            const colIndex = cell.dataset.col; 

            let currentDate = new Date(baseDate);
            currentDate.setDate(baseDate.getDate() - baseDate.getDay() + parseInt(colIndex));


            const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
            
            const startTime = timeSlots[rowIndex].split('-')[0]; 

            selectedTimeslots.push({ date: formattedDate, start_time: startTime });
        });

        form.querySelector('[name="date"]').value = "";
        form.querySelector('[name="start_time"]').value = "";
        selectedTimeslots.forEach((timeslot, index) => {
        form.querySelector('[name="date"]').value += timeslot.date + (index < selectedTimeslots.length - 1 ? ',' : '');  
        form.querySelector('[name="start_time"]').value += timeslot.start_time + (index < selectedTimeslots.length - 1 ? ',' : '');  
    });        
        form.submit();
    }

    function toggleTimeSlotCellColour(timeSlotCell) {
        timeSlotCell.classList.toggle("filled")
    }

    function resetCells() {
        const allCells = document.querySelectorAll("#availability-table td");
        allCells.forEach(cell => {
            cell.classList.remove("filled");
        });
    }

    const timeSlotColour = document.createElement('style');
    timeSlotColour.innerHTML = `
        .filled {
            background-color: lightblue;  
        }
    `;
    
    document.head.appendChild(timeSlotColour);
    document.getElementById("resetButton").addEventListener("click", resetCells);
    document.getElementById("saveButton").addEventListener("click", saveState);
})
