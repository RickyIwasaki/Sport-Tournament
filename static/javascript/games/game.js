
const copyToClipboard = () => {
    const gameId = document.querySelector('#game_id');
    navigator.clipboard.writeText(gameId.textContent);
    console.log(gameId.textContent);
};
const clipboardIcon = document.querySelector('.fa-clipboard');
clipboardIcon.addEventListener('click', copyToClipboard);
