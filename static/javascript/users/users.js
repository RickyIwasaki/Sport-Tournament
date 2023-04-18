
let statuses = true;

const addListDisplay = async () => {
    let response;
    response = await axios.get(`/users/api/${statuses}`);
    
    const displayList = document.querySelector('#list-display');
    for(let row of response.data){
        const newLinkRow = document.createElement('a');
        newLinkRow.setAttribute('href', `users/${row[0]}`);
        displayList.appendChild(newLinkRow);

        let newDivRow = document.createElement('div');
        newDivRow.classList.add('row');
        newLinkRow.appendChild(newDivRow);

        let newDivRowDiv = document.createElement('div');
        newDivRow.appendChild(newDivRowDiv);

        let rowClasses = ['row-id', 'row-username', 'row-region', 'row-status'];
        for(let index in row){
            const newSpan = document.createElement('span');
            newSpan.classList.add(rowClasses[index]);
            newSpan.textContent = row[index];
            newDivRowDiv.appendChild(newSpan);
        }
    }   
}

const removeListDisplay = () => {
    const listDisplay = document.querySelector('#list-display');
    while(listDisplay.firstChild){
        listDisplay.firstChild.remove();
    }
}

const handleFriendsCheckChange = () => {
    if(statuses){
        statuses = false;
    }
    else{
        statuses = true;
    }
    removeListDisplay();
    addListDisplay();
}
const friendsCheckbox = document.querySelector('#friends');
friendsCheckbox.addEventListener('change', handleFriendsCheckChange);

//do scroll rubber banding with extra rows loading in instead of loading everything at once
//limit to 10 row per load
//info icon hover show description
