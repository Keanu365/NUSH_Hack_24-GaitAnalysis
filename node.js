// const constraints = {
//     video: true
// };
// const video = document.querySelector('video');
// function handleSuccess(stream) {
//     video.srcObject = stream;
// }
// function handleError(error) {
//     console.error('Reeeejected!', error);
// }
// navigator.mediaDevices.getUserMedia(constraints).
// then(handleSuccess).catch(handleError);

const constraints = { video: true };
const video = document.getElementById('video');
const canvas = document.querySelector('canvas');
const responseP = document.getElementById('recog_text');
let context = canvas.getContext('2d');

// Handle successful video stream
function handleSuccess(stream) {
    video.srcObject = stream;
    captureFrame();  // Start capturing frames for analysis
}

// Handle error in accessing webcam
function handleError(error) {
    console.error('Error accessing webcam:', error);
}

// Periodically capture frame and send for analysis
function captureFrame() {
    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current frame from video onto canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert frame to data URL
    const imageData = canvas.toDataURL('image/jpeg');
    console.log(imageData)

    // Send frame for analysis
    analyzeFrame(imageData);

    // Capture the next frame after a delay (e.g., every 500 ms)
    setTimeout(captureFrame, 250);
}

// Send the frame to server for analysis
async function analyzeFrame(imageData) {
    try {
        const response = await fetch('http:localhost:3000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });
        const result = await response.json();
        if(result.analysis == "NA"){
            responseP.textContent = "No person detected"
        }else{
            responseP.textContent = 'Please enter ' + result.analysis;
        }
    } catch (error) {
        console.error('Error analyzing frame:', error);
    }
}

navigator.mediaDevices.getUserMedia(constraints)
    .then(handleSuccess)
    .catch(handleError);