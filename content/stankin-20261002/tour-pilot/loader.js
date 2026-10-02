import('./tour.js').catch(error => {
document.querySelector('.loading-title').textContent='Не удалось запустить просмотр';
document.getElementById('progress').hidden=true;
document.getElementById('load-text').textContent='Проверьте соединение и попробуйте ещё раз.';
const retry=document.getElementById('retry');retry.hidden=false;retry.onclick=()=>location.reload();
console.error(error);
});