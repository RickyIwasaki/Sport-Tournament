
const copyToClipboard = () => {
    const tournamentId = document.querySelector('#tournament_id');
    navigator.clipboard.writeText(tournamentId.textContent);
    console.log(tournamentId.textContent);
};
const clipboardIcon = document.querySelector('.fa-clipboard');
clipboardIcon.addEventListener('click', copyToClipboard);
