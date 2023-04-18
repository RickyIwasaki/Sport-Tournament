
const loadSportNewsData = async () => {
    const response = await axios.get('/home/api');

    const list = document.querySelector('.sport_news_list');

    for(let article of response.data.articles){
        const newA = document.createElement('a');
        list.appendChild(newA);
        newA.setAttribute('href', article.url);
    
        const newDiv = document.createElement('div');
        newDiv.classList.add('row');
        newA.appendChild(newDiv);

        let newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('title');
        newP.textContent = article.title;
    
        newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('name');
        newP.textContent = article.source.name;
    
        newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('author');
        newP.textContent = article.author;
    
        newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('publishedAt');
        newP.textContent = article.publishedAt;
    
        newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('description');
        newP.textContent = article.description;
        
        newP = document.createElement('p');
        newDiv.appendChild(newP);
        newP.classList.add('content');
        newP.textContent = article.content;
    }


}

loadSportNewsData();




























