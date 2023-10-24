export default function runPromisesSequentially(
  promisesWithDeps: (() => Promise<unknown>)[],
): Promise<unknown[]> {
  return promisesWithDeps.reduce(async (promise: Promise<unknown[]>, func) => {
    const result = await promise;
    const r = await func();
    return result.concat(r);
  }, Promise.resolve([]));
}
