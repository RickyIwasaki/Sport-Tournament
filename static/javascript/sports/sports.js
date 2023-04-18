
const handleAddStatusClick = (event) => {
    event.preventDefault();
    const statusListTable = document.querySelector('#type_status_list').children[0];
    const newTr = document.createElement('tr');
    statusListTable.appendChild(newTr);

    const newLabel = document.createElement('label');
    newLabel.setAttribute('for', `${statusListTable.children.length}`);
    newLabel.textContent = `status ${statusListTable.children.length}`;

    const newInput = document.createElement('input');
    newInput.setAttribute('type', 'text');
    newInput.setAttribute('name', `status ${statusListTable.children.length}`)
    newInput.id = `${statusListTable.children.length}`;
    newInput.setAttribute('placeholder', 'status');

    let newTd = document.createElement('td');
    newTd.appendChild(newLabel);
    newTr.appendChild(newTd);

    newTd = document.createElement('td');
    newTd.appendChild(newInput);
    newTr.appendChild(newTd);
}
const addStatusBtn = document.querySelector('#add-status-input');
addStatusBtn.addEventListener('click', handleAddStatusClick);
