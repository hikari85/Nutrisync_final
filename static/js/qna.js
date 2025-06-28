// static/js/qna.js
const questions = document.querySelectorAll('.qna-question');
questions.forEach(question => {
    question.addEventListener('click', () => {
        const parentItem = question.parentElement;
        parentItem.classList.toggle('active');
    });
});
