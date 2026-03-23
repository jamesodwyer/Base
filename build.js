import { register } from '@tokens-studio/sd-transforms';
import StyleDictionary from 'style-dictionary';

register(StyleDictionary);

const sd = new StyleDictionary({
  ...JSON.parse((await import('fs')).readFileSync('style-dictionary.config.json', 'utf-8')),
  log: { verbosity: 'default', warnings: 'warn', errors: { brokenReferences: 'console' } },
});
await sd.buildAllPlatforms();
