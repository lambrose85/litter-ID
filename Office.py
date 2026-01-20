
import Log

def main():
    import cv2 as cv
    import numpy as np
    # Open the default camera
    cam = cv.VideoCapture(0)
    bg_subtractor = cv.createBackgroundSubtractorKNN(history=500,dist2Threshold=400,detectShadows=True)
# Get the default frame width and height
    frame_width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

    while True:
        ret, frame = cam.read()


   #apply background subtraction 
        fg_mask = bg_subtractor.apply(frame)
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))
        fg_mask = cv.morphologyEx(fg_mask, cv.MORPH_OPEN, kernel)
        fg_mask = cv.dilate(fg_mask, kernel, iterations=2)
    
    # Find contours
        contours, _ = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # Create a copy for drawing
        highlighted_frame = frame.copy()
    
        for contour in contours:
        # Filter small contours (noise)
            if cv.contourArea(contour) > 500:  # Minimum area threshold
            # Get bounding rectangle
                x, y, w, h = cv.boundingRect(contour)
            
            # Method 1: Draw colored bounding box
                cv.rectangle(highlighted_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add label
                cv.putText(highlighted_frame, 'Motion', (x, y-10), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
        cv.imshow('Original', frame)
        cv.imshow('Foreground Mask', fg_mask)
        cv.imshow('Highlighted Objects', highlighted_frame)
    
        if cv.waitKey(30) & 0xFF == ord('q'):
            break
    # Write the frame to the output file
        out.write(frame)

  

    # Press 'q' to exit the loop
        if cv.waitKey(1) == ord('q'):
         break

# Release the capture and writer objects
    cam.release()
    out.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
