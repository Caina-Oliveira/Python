import CSVWriter from './CSVWriter';
import FileWriter from './FileWriter';
import JSONWriter from './JSONWriter';

export default function getInstance(writeMode: string): FileWriter {
  if (writeMode != null && 'CSV'.includes(writeMode.toUpperCase())) {
    return new CSVWriter();
  }
  return new JSONWriter();
}
