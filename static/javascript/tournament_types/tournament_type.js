
const handleAddStatusClick = (event) => {
    event.preventDefault();
    const statusesTable = document.querySelector('#statuses').children[0];
    const newTr = document.createElement('tr');
    statusesTable.appendChild(newTr);

    const newLabel = document.createElement('label');
    newLabel.setAttribute('for', `${statusesTable.children.length}`);
    newLabel.textContent = `status ${statusesTable.children.length}`;

    const newInput = document.createElement('input');
    newInput.setAttribute('type', 'text');
    newInput.setAttribute('name', `status ${statusesTable.children.length}`)
    newInput.id = `${statusesTable.children.length}`;
    newInput.setAttribute('placeholder', 'status');

    let newTd = document.createElement('td');
    newTd.appendChild(newLabel);
    newTr.appendChild(newTd);

    newTd = document.createElement('td');
    newTd.appendChild(newInput);
    newTr.appendChild(newTd);
}
const addStatusBtn = document.querySelector('#add-status');
addStatusBtn.addEventListener('click', handleAddStatusClick);
