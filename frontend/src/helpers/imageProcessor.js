export function extractGridFromImage(imageSrc, width = 64, height = 64) {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.src = imageSrc;

    img.onload = () => {
      // Create a canvas object offscreen
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;

      const context = canvas.getContext("2d");

      // Create a 64x64 image
      context.drawImage(img, 0, 0, width, height);

      // Extract the pixels
      // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData
      const imageData = context.getImageData(0, 0, width, height);
      // Pixels is a 1D array. Each pixel has 4 values (R (red), G (green), B (blue), and A (alpha)).
      // These values are appeneded to the array side by side
      const pixels = imageData.data;

      // Transform 1D array into 2D array
      const grid = [];

      for (let y = 0; y < height; y++) {
        const row = [];

        for (let x = 0; x < width; x++) {
          // Calculate the index in the 1D array

          const index = (y * width + x) * 4;

          // Grab the Red value (pixels[index] is Red, index+1 is Green, index+2 is Blue, index+3 is Alpha)

          const a = pixels[index + 3];

          // Transparent pixel. It's an open space.
          if (a < 128) {
            row.push(0);
          } else {
            row.push(1);
          }
        }
        grid.push(row);
      }

      resolve(grid);
    };

    img.onerror = () => {
      reject(new Error("Failed to load the map image."));
    };
  });
}

// Old logic I might need later
// const r = pixels[index];
// const g = pixels[index + 1];
// const b = pixels[index + 2];
// // Get the brightness of the pixel
// const average = (r + g + b) / 3;

// // If the brightness is dark (less than 128), it's a wall (1).
// // If it's bright (greater than 128), it's open space (0).
// const isWall = average < 128 ? 1 : 0;

// row.push(isWall);
