
let statuses = [];
let term = '';

const addListDisplay = async () => {
    let response;
    response = await axios.get(`/tournaments/api/${statuses}`);
    
    const displayList = document.querySelector('#list-display');
    for(let row of response.data){
        const newLinkRow = document.createElement('a');
        newLinkRow.setAttribute('href', `tournaments/${row[1]}`);
        displayList.appendChild(newLinkRow);

        let newDivRow = document.createElement('div');
        newDivRow.classList.add('row');
        newLinkRow.appendChild(newDivRow);

        let newDivRowDiv = document.createElement('div');
        newDivRow.appendChild(newDivRowDiv);

        let rowClasses = ['row-name', 'row-id', 'row-type', 'row-creator', 'row-status'];
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
