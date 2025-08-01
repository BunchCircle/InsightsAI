const fs = require('fs-extra');
const path = require('path');

async function copyBuildFiles() {
  const sourceDir = path.join(__dirname, '../out');
  const targetDir = path.join(__dirname, '../out');

  try {
    // Ensure target directory exists
    await fs.ensureDir(targetDir);

    // Copy files
    await fs.copy(sourceDir, targetDir, {
      overwrite: true,
    });

    console.log('Successfully copied build files');
  } catch (error) {
    console.error('Error copying build files:', error);
    process.exit(1);
  }
}

copyBuildFiles();
