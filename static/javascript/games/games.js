
let statuses = [];
let term = '';

const addListDisplay = async () => {
    let response;
    response = await axios.get(`games/api/${statuses}`);
    const displayList = document.querySelector('#list-display');

    rowClasses = ['row-name', 'row-id', 'row-tournament', 'row-tournament-type', 'row-sport', 'row-creator', 'row-status'];
    for(let rowIndex in response.data){
        const newLinkRow = document.createElement('a');
        newLinkRow.setAttribute('href', `games/${response.data[rowIndex][1]}`);
        displayList.appendChild(newLinkRow);

        let newDivRow = document.createElement('div');
        newDivRow.classList.add('row');
        newLinkRow.appendChild(newDivRow);

        let newDivRowDiv = document.createElement('div');
        newDivRow.appendChild(newDivRowDiv);

        for(let itemIndex in response.data[rowIndex]){
            const newSpan = document.createElement('span');
            newSpan.classList.add(rowClasses[itemIndex]);
            newSpan.textContent = response.data[rowIndex][itemIndex];
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

const handleOpenCheckChange = () => {
    if(statuses.includes('publicly open')){
        statuses.splice(statuses.indexOf('publicly open'), 1);
    }
    else{
        statuses[statuses.length] = 'publicly open';
    }
    removeListDisplay();
    addListDisplay();
}
const openCheckbox = document.querySelector('#publicly_open');
openCheckbox.addEventListener('change', handleOpenCheckChange);

const handleprivateCheckChange = () => {
    if(statuses.includes('private')){
        statuses.splice(statuses.indexOf('private'), 1);
    }
    else{
        statuses[statuses.length] = 'private';
    }
    removeListDisplay();
    addListDisplay();
}
const privateCheckbox = document.querySelector('#private');
privateCheckbox.addEventListener('change', handleprivateCheckChange);

//do scroll rubber banding with extra rows loading in instead of loading everything at once
//limit to 10 row per load
//info icon hover show description
