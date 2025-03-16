document.addEventListener('DOMContentLoaded', function() {
    const location1Select = document.getElementById('location1');
    const location2Select = document.getElementById('location2');

    function populateLocation1() {
        fetch('http://localhost:5000/get_locations', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Received Location1 data:', data);

                location1Select.innerHTML = ''; // Clear existing options

                if (data.location1_options && data.location1_options.length > 0) {
                    data.location1_options.forEach(loc => {
                        const option = document.createElement('option');
                        option.value = loc.toLowerCase();
                        option.textContent = loc.charAt(0).toUpperCase() + loc.slice(1);
                        location1Select.appendChild(option);
                    });

                    location1Select.dispatchEvent(new Event('change'));
                } else {
                    console.warn('No location1 options received');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                location1Select.innerHTML = '<option>Error loading locations</option>';
            });
    }

    // Populate Location2 based on Location1 selection
    location1Select.addEventListener('change', function() {
        const selectedLocation1 = this.value;
        console.log('Selected Location1:', selectedLocation1);

        fetch(`http://127.0.0.1:5000/get_locations?location1=${selectedLocation1}`)
            .then(response => response.json())
            .then(data => {
                console.log('Received Location2 data:', data);

                location2Select.innerHTML = ''; // Clear existing options

                if (data.location2_options && data.location2_options.length > 0) {
                    data.location2_options.forEach(loc => {
                        const option = document.createElement('option');
                        option.value = loc.toLowerCase();
                        option.textContent = loc;
                        location2Select.appendChild(option);
                        console.log('Added Location2 option:', loc);
                    });
                } else {
                    console.error('No location2 options received');
                }
            })
            .catch(error => {
                console.error('Error fetching Location2:', error);
            });
    });

    populateLocation1();
});

function validateFloors() {
    const currentFloor = document.getElementById('current_floor');
    const totalFloors = document.getElementById('total_from');

    // Remove any existing error messages
    const existingError = document.getElementById('floor-error');
    if (existingError) {
        existingError.remove();
    }

    // Check if current floor is greater than total floors
    if (parseInt(currentFloor.value) > parseInt(totalFloors.value)) {
        // Create error message
        const errorMsg = document.createElement('div');
        errorMsg.id = 'floor-error';
        errorMsg.style.color = 'red';
        errorMsg.style.marginBottom = '10px';
        errorMsg.textContent = 'Current floor cannot be greater than total floors';

        // Insert error message after total floors input
        totalFloors.parentNode.insertBefore(errorMsg, totalFloors.nextSibling);

        return false;
    }

    return true;
}


function predictPrice() {
    if (!validateFloors()) {
        return;
    }

    let data = {
        area: parseFloat(document.getElementById("area").value),
        room_size: parseFloat(document.getElementById("total_rooms").value),
        current_floor: parseInt(document.getElementById("current_floor").value),
        total_from: parseInt(document.getElementById("total_from").value),
        building_type: document.getElementById("building_type").value,
        bill_of_sale: document.getElementById("bill_of_sale").value,
        repair_status: document.getElementById("repair_status").value,
        Location1: document.getElementById("location1").value,
        Location2: document.getElementById("location2").value
    };

    fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById("result").innerHTML =
                "Predicted Price: <strong>" + data.predicted_price + " AZN</strong>";
        })
        .catch(error => {
            document.getElementById("result").innerHTML =
                "<span style='color:red;'>Error: " + error + "</span>";
        });
}

function clearForm() {
    // Reset all form inputs
    document.getElementById('location1').selectedIndex = 0;
    document.getElementById('location2').selectedIndex = 0;
    document.getElementById('area').value = '';
    document.getElementById('total_rooms').value = '';
    document.getElementById('current_floor').value = '';
    document.getElementById('total_from').value = '';
    document.getElementById('building_type').selectedIndex = 0;
    document.getElementById('bill_of_sale').selectedIndex = 0;
    document.getElementById('repair_status').selectedIndex = 0;

    document.getElementById('result').innerHTML = '';
}