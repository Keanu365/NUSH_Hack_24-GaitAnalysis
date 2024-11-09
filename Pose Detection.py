import cv2 as cv
import numpy as np

# Define the body parts and their corresponding indices
BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

# Define the pairs of body parts that form a pose
POSE_PAIRS = [ ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"] ]

# Define input dimensions for the network
width = 368
height = 368
inWidth = width
inHeight = height

# Lists to store locations of ellipses
coordPointsFrom = []
coordPointsTo = []

# Load the pre-trained pose detection model
net = cv.dnn.readNetFromTensorflow("graph_opt.pb")
thr = 0.2  # Confidence threshold for the detected keypoints

# Load webcam
cap = cv.VideoCapture(0)

# Function to detect poses in a frame
def poseDetector(frame):
    frameWidth =  frame.shape[1]
    frameHeight = frame.shape[0]

    # Prepare the input blob for the network
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    # Iterate over the body parts to extract keypoints
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body part
        heatMap = out[0, i, :, :]

        # Find the maximum confidence and corresponding location
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        points.append((int(x), int(y)) if conf > thr else None)

    # Connect keypoints to form poses
    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            # Draw keypoints
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            if len(coordPointsFrom) > 0:
                for i in coordPointsFrom:
                    cv.ellipse(frame, i, (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
                for i in coordPointsTo:
                    cv.ellipse(frame, i, (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            coordPointsFrom.append(points[idFrom])
            coordPointsTo.append(points[idTo])
            if len(coordPointsFrom) > 24:
                del coordPointsFrom[0]
                del coordPointsTo[0]
    t, _ = net.getPerfProfile()

    return frame

while True:
    ret, frame = cap.read()
    
    output = poseDetector(frame)
    
    cv.imshow("Frame", output)
    
    if cv.waitKey(1) == ord("q"):
        break

cap.release()
cv.destroyAllWindows()