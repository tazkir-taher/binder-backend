//selecting all required elements
const dropArea2 = document.querySelector(".drag-area2"),
    dragText2 = dropArea2.querySelector("header"),
    button2 = dropArea2.querySelector("button"),
    input2 = dropArea2.querySelector("input");
let file2; //this is a global variable and we'll use it inside multiple functions

button2.onclick = () => {
    input2.click(); //if user click on the button then the input also clicked
}

input2.addEventListener("change", function () {
    //getting user select file2 and [0] this means if user select multiple files then we'll select only the first one
    console.log(this.files)
    file2 = this.files[0];
    console.log(file2);
    // $("#product_img").val(file2.name);
    dropArea2.classList.add("active");
    showFile2(); //calling function
});


//If user Drag File Over dropArea2
dropArea2.addEventListener("dragover", (event) => {
    event.preventDefault(); //preventing from default behaviour
    dropArea2.classList.add("active");
    dragText2.textContent = "Release to Upload File";
});

//If user leave dragged File from dropArea2
dropArea2.addEventListener("dragleave", () => {
    dropArea2.classList.remove("active");
    dragText2.textContent = "Drag & Drop to Upload File";
});

//If user drop File on dropArea2
dropArea2.addEventListener("drop", (event) => {
    event.preventDefault(); //preventing from default behaviour
    //getting user select file2 and [0] this means if user select multiple files then we'll select only the first one
    file2 = event.dataTransfer.files[0];
    showFile2(); //calling function
});

function showFile2() {
    let fileType = file2.type; //getting selected file2 type
    let validExtensions = ["image/jpeg", "image/jpg", "image/png"]; //adding some valid image extensions in array
    if (validExtensions.includes(fileType)) { //if user selected file2 is an image file2
        let fileReader = new FileReader(); //creating new FileReader object
        fileReader.onload = () => {
            let fileURL = fileReader.result; //passing user file2 source in fileURL variable
            $("#product_img2").val(fileURL);
            // UNCOMMENT THIS BELOW LINE. I GOT AN ERROR WHILE UPLOADING THIS POST SO I COMMENTED IT
            //creating an img tag and passing user selected file2 source inside src attribute
            try {
                dropArea2.innerHTML = `<img src="${fileURL}" alt="image">`; //adding that created img tag inside dropArea2 container
            } catch (e) {
                console.log(e);
            }
        }
        fileReader.readAsDataURL(file2);
    } else {
        let fileReader = new FileReader(); //creating new FileReader object
        fileReader.onload = () => {
            let fileURL = fileReader.result; //passing user file2 source in fileURL variable
            dragText2.textContent = `Selected File: ${file2.name}`;
            $("#product_img2").val(fileURL);
        }
        fileReader.readAsDataURL(file2);
    }
}