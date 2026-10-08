if(new URLSearchParams(location.search).get('embed')==='1')document.documentElement.classList.add('embedded');
import('./tour.js?v=20261008-contrast1').catch(error => {
document.querySelector('.loading-title').textContent='Не удалось запустить просмотр';
document.getElementById('progress').hidden=true;
document.getElementById('load-text').textContent='Проверьте соединение и попробуйте ещё раз.';
const retry=document.getElementById('retry');retry.hidden=false;retry.onclick=()=>location.reload();
console.error(error);
});