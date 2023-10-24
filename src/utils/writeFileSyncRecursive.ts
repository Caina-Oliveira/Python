import fs from 'fs';
import path from 'path';

export default function writeFileSyncRecursive(filename: string, content: string | Buffer): void {
  const folders = filename.split(path.sep).slice(0, -1);

  if (folders.length) {
    // create folder path if it doesn't exist
    folders.reduce((last, folder) => {
      const folderPath = last + folder + path.sep;
      if (!fs.existsSync(folderPath)) {
        fs.mkdirSync(folderPath);
      }
      return folderPath;
    }, '/');
  }

  fs.writeFileSync(filename, content);
}
