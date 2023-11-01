let personalInfo = JSON.parse(localStorage.getItem('personalInfo'));;

// const personalInfo = {
//     Gender: "Male",
//     Age: "23",
//     // birthday: "2000-6-25",
//     Occupation: "student",
//     Education: "Texas A&M University",
//     Location: "TX",
// } 
const username = personalInfo.DisplayName;

function refresh_userInfo() {
    personalInfo = JSON.parse(localStorage.getItem('personalInfo'));
    const displayNameSpan = document.querySelector('.DisplayName2')
    displayNameSpan.textContent = personalInfo.DisplayName

    const genderSpan = document.querySelector('.Gender');
    genderSpan.textContent = personalInfo.Gender;

    const ageBirthSpan = document.querySelector('.Age-Birth');
    // ageBirthSpan.textContent = '23 | 2000-6-25';
    ageBirthSpan.textContent = personalInfo.Age;

    const occupationSpan = document.querySelector('.Occupation');
    occupationSpan.textContent = personalInfo.Occupation;

    const educationSpan = document.querySelector('.Education');
    educationSpan.textContent = personalInfo.Education;

    const locationSpan = document.querySelector('.Location');
    locationSpan.textContent = personalInfo.Location;

    // window.alert(localStorage.getItem("following_counts"));
    // window.alert(localStorage.getItem("followed_counts"));
    const followingCounterSpan = document.getElementById('followingCounter');
    followingCounterSpan.textContent = localStorage.getItem("following_counts");

    const followerCounterSpan = document.getElementById('followerCounter');
    followerCounterSpan.textContent = localStorage.getItem("followed_counts");
}

refresh_userInfo();

const editProfileBtn = document.getElementById('editProfileButton');
const editProfileModal = document.getElementById('editProfileModal');
const editProfileCloseModalBtn = document.getElementById('editProfileCloseModalBtn');

editProfileBtn.addEventListener('click', () => {
    attributes = ["Gender", 'Age-Birth', 'Occupation', 'Education', 'Location'];
    attributes.forEach(attribute => {
        element = document.querySelector('.' + attribute);
        spanElement = document.querySelector('.' + attribute + 'Modal');
        spanElement.textContent = element.textContent;
    });
    editProfileModal.style.display = 'block';
});

editProfileCloseModalBtn.addEventListener('click', () => {
    editProfileModal.style.display = 'none';
});

window.addEventListener('click', (event) => {
    if (event.target === editProfileModal) {
        editProfileModal.style.display = 'none';
    }
});

function updateAttribute(className, inputId) {
    inputElement = document.getElementById(inputId);
    inputValue = inputElement.value;

    //todo
    if (className == "Age-Birth") {
        attr = "Age";
        val = parseInt(inputValue);
    } else {
        attr = className;
        val = inputValue;
    };

    fetch('/userinfo', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            userID: parseInt(localStorage.getItem("userID")),
            attr: attr,
            value: val,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            localStorage.setItem('personalInfo', JSON.stringify(data.data.personal_info));
        } else {
            alert("Invalid update");
        }
    })
    .catch((error) => console.error('Error:', error));

    spanElementModal = document.querySelector('.' + className + 'Modal');
    spanElement = document.querySelector('.' + className);
    if (inputValue.trim() !== '') {

        spanElement.textContent = inputValue;
        spanElementModal.textContent = inputValue;
    }
}