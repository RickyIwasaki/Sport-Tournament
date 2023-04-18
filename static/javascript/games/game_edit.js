
const tournamentSelect = document.querySelector('#tournament');
const changeSelectInput = async () => {
    tournament_id = tournamentSelect.value.substring(0, tournamentSelect.value.indexOf(' :'));
    let response;
    response = await axios.get(`/tournament_types/api/tournament/${tournament_id}`);
    
    const tournamentStatusSelect = document.querySelector('#tournament_game_status');
    while(tournamentStatusSelect.lastChild){
        tournamentStatusSelect.lastChild.remove();
    }
    for(let status of response.data){
        newOption = document.createElement('option');
        tournamentStatusSelect.appendChild(newOption);
        newOption.textContent = status;
    }   
}
tournamentSelect.addEventListener('change', changeSelectInput);

changeSelectInput();
