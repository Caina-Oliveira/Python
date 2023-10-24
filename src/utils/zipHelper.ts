import fs from 'fs';
import JSZip from 'jszip';
import path from 'path';

import writeFileSyncRecursive from './writeFileSyncRecursive';

export async function zipFolder(
  dirPath: string,
  files: string[],
  zipFilename: string,
): Promise<void> {
  const zip = new JSZip();

  files.forEach((file) => {
    zip.file(`${file}`, fs.readFileSync(path.resolve(dirPath, file)));
  });

  const generatedFile = await zip.generateAsync({ type: 'nodebuffer', streamFiles: true });

  writeFileSyncRecursive(path.resolve(dirPath, zipFilename), generatedFile);
}
