const fs = require('fs');
const content = fs.readFileSync('scripts/parse_test.py', 'utf8');
const startIdx = content.indexOf('raw_data = """') + 'raw_data = """'.length;
const endIdx = content.indexOf('"""\n\nlines');
const text = content.substring(startIdx, endIdx).trim();
const lines = text.split('\n').filter(l => l.trim());
console.log('Total lines:', lines.length);

lines.forEach((l, idx) => {
  const parts = l.split('\t');
  console.log('--- Line', idx, parts[0].trim());
  console.log('Total tabs+1 (parts):', parts.length);
  const nonEmpties = parts.map((p, i) => ({ col: i, val: p.trim() })).filter(x => x.val);
  console.log('Non empties:', JSON.stringify(nonEmpties));
});
