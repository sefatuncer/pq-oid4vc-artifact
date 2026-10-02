#!/usr/bin/env python3
"""Show that changed code files differ from a base revision only in comments, docstrings and
messages written to stderr (usage and error messages).

For every code file that differs between the base revision and the working tree, both versions are
reduced to their code tokens: comments are removed (language-aware, string literals are respected),
Python docstrings are removed (comparison of the abstract syntax trees), whitespace is ignored. The
token sequences must then be identical. The only accepted exception is a changed string literal on a
line that writes to stderr (for example `fwrite(STDERR, ...)`, `Console.Error.WriteLine(...)`,
`print(..., file=sys.stderr)`, `>&2`) or a usage message that starts with "usage:".

Usage: python tools/verify_comment_only.py [--base REV] [--list] [path ...]
       (default base: main; default paths: every changed code file)
Exit code 0 if no file has a code difference. Standard library only (git must be on PATH).
"""
import argparse
import ast
import difflib
import io
import os
import re
import subprocess
import sys

CODE_EXT = {'.py', '.sh', '.bash', '.mjs', '.js', '.ts', '.go', '.java', '.kt', '.kts', '.rb', '.php',
            '.cs', '.dart', '.ex', '.exs', '.rs', '.swift', '.c', '.h', '.lp', '.spthy', '.pv', '.pvt',
            '.toml', '.awk'}
STDERR_MARK = re.compile(r'STDERR|stderr|Console\.Error|System\.err|eprintln!|eprint!|os\.Stderr|>&2|'
                         r'standardError|console\.error|\$stderr|IO\.puts\(:stderr|ADAPTOR_HATA_TAM')


def git(*args):
    r = subprocess.run(['git', *args], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def language(path):
    name = os.path.basename(path)
    if name == 'Dockerfile' or name.startswith('Dockerfile.'):
        return 'docker'
    ext = os.path.splitext(name)[1].lower()
    if ext == '.py':
        return 'python'
    if ext in ('.sh', '.bash'):
        return 'shell'
    if ext in ('.rb',):
        return 'ruby'
    if ext in ('.ex', '.exs'):
        return 'elixir'
    if ext in ('.toml', '.awk'):
        return 'hash'
    if ext == '.lp':
        return 'asp'
    if ext in ('.pv', '.pvt'):
        return 'proverif'
    if ext == '.php':
        return 'php'
    if ext == '.rs':
        return 'rust'
    return 'clike'          # c, cs, java, kt, kts, go, swift, dart, js, mjs, ts, spthy


# ---------------------------------------------------------------- lexer
def lex(text, lang):
    """Return a list of (token, line_text, is_string) with comments removed."""
    lines = text.split('\n')
    toks = []
    i, n, line_no = 0, len(text), 0
    line_start = [0]
    for k, ch in enumerate(text):
        if ch == '\n':
            line_start.append(k + 1)

    def line_of(pos):
        lo, hi = 0, len(line_start) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_start[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lines[lo] if lo < len(lines) else ''

    hash_comment = lang in ('shell', 'ruby', 'elixir', 'hash', 'php', 'docker', 'python')
    slash_comment = lang in ('clike', 'php', 'rust')
    while i < n:
        c = text[i]
        # comments
        if lang == 'docker':
            if (i == 0 or text[i - 1] == '\n'):
                j = i
                while j < n and text[j] in ' \t':
                    j += 1
                if j < n and text[j] == '#':
                    e = text.find('\n', j)
                    i = n if e < 0 else e
                    continue
        elif hash_comment and c == '#':
            prev = text[i - 1] if i > 0 else '\n'
            is_comment = True
            if lang == 'shell' and not (prev in ' \t\n;(|&'):
                is_comment = False                       # ${#var}, $#, a#b
            if lang == 'elixir' and i + 1 < n and text[i + 1] == '{':
                is_comment = False
            if is_comment:
                e = text.find('\n', i)
                i = n if e < 0 else e
                continue
        if slash_comment and text.startswith('//', i):
            e = text.find('\n', i)
            i = n if e < 0 else e
            continue
        if slash_comment and text.startswith('/*', i):
            e = text.find('*/', i + 2)
            i = n if e < 0 else e + 2
            continue
        if lang == 'asp' and c == '%':
            if text.startswith('%*', i):
                e = text.find('*%', i + 2)
                i = n if e < 0 else e + 2
            else:
                e = text.find('\n', i)
                i = n if e < 0 else e
            continue
        if lang == 'proverif' and text.startswith('(*', i):
            e = text.find('*)', i + 2)
            i = n if e < 0 else e + 2
            continue
        if c.isspace():
            i += 1
            continue
        # strings
        if lang == 'rust' and c == 'r' and re.match(r'r#*"', text[i:i + 10]):
            m = re.match(r'r(#*)"', text[i:])
            close = '"' + m.group(1)
            e = text.find(close, i + len(m.group(0)))
            e = n if e < 0 else e + len(close)
            toks.append((text[i:e], line_of(i), True))
            i = e
            continue
        for q in ('"""', "'''"):
            if text.startswith(q, i) and lang in ('python', 'clike', 'elixir', 'php', 'ruby'):
                e = text.find(q, i + 3)
                e = n if e < 0 else e + 3
                toks.append((text[i:e], line_of(i), True))
                i = e
                break
        else:
            q = None
            if c in '"`' or (c == "'" and lang != 'rust'):
                q = c
            elif c == "'" and lang == 'rust':
                m = re.match(r"'(\\.|[^\\'\n])'", text[i:])
                if m:
                    toks.append((m.group(0), line_of(i), True))
                    i += len(m.group(0))
                    continue
            if c == '@' and i + 1 < n and text[i + 1] == '"' and lang == 'clike':
                j = i + 2
                while j < n:
                    if text[j] == '"' and j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    if text[j] == '"':
                        break
                    j += 1
                toks.append((text[i:j + 1], line_of(i), True))
                i = j + 1
                continue
            if q is not None and not (lang == 'shell' and q == "'" and False):
                j = i + 1
                depth = 0
                while j < n:
                    ch = text[j]
                    if ch == '\\' and not (lang == 'shell' and q == "'"):
                        j += 2
                        continue
                    if lang == 'elixir' and q == '"' and text.startswith('#{', j):
                        depth += 1
                        j += 2
                        continue
                    if depth and ch == '}':
                        depth -= 1
                        j += 1
                        continue
                    if ch == q and not depth:
                        break
                    j += 1
                toks.append((text[i:j + 1], line_of(i), True))
                i = j + 1
                continue
            # identifiers, numbers, punctuation
            m = re.match(r'[A-Za-z_À-￿][\wÀ-￿]*|\d[\w.]*|\S', text[i:])
            toks.append((m.group(0), line_of(i), False))
            i += len(m.group(0))
            continue
        continue
    return toks


def allowed_string_change(old_tok, new_tok):
    (ot, ol, os_), (nt, nl, ns) = old_tok, new_tok
    if not (os_ and ns):
        return False
    if STDERR_MARK.search(nl) and STDERR_MARK.search(ol):
        return True
    body = nt.strip('\'"`')
    return body.lower().startswith('usage:')


QUOTES = '"' + "'"
HEREDOC = re.compile(r'<<-?\s*[' + QUOTES + r']?([A-Za-z_][A-Za-z0-9_]*)[' + QUOTES + r']?')
PREPROC = re.compile(r'\s*#\s*(include|define|if|ifdef|ifndef|endif|else|elif|pragma|undef)\b')
SHELL_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"' + r"|'[^']*'" + r'|[A-Za-z_À-￿][\wÀ-￿]*|\d[\w.]*|\S')


def strip_shell(text):
    """Line-based comment removal for shell scripts, including full-line comments of code embedded
    in here-documents (`//`, `#`, `/* */` lines; C preprocessor lines are kept)."""
    out, delim, strip_tabs = [], None, False
    for line in text.split('\n'):
        s = line.strip()
        if delim is not None:
            if (s if strip_tabs else line) == delim:
                delim = None
                out.append(line)
                continue
            if (s.startswith('//') or s.startswith('/*') or s.startswith('*') or
                    (s.startswith('#') and not PREPROC.match(line) and not s.startswith('#!'))):
                continue
            out.append(line)
            continue
        if s.startswith('#'):
            continue
        # trailing comment: ' #' outside quotes
        q, cut = None, None
        for k, ch in enumerate(line):
            if q:
                if ch == q and (q == "'" or line[k - 1] != '\\'):
                    q = None
            elif ch in QUOTES:
                q = ch
            elif ch == '#' and k > 0 and line[k - 1] in ' \t':
                cut = k
                break
        if cut is not None:
            line = line[:cut]
        m = HEREDOC.search(line)
        if m and '<<<' not in line:
            delim, strip_tabs = m.group(1), '<<-' in line
        out.append(line)
    return '\n'.join(out)


def line_tokens(text):
    toks = []
    for line in text.split('\n'):
        for m in SHELL_TOKEN.finditer(line):
            t = m.group(0)
            toks.append((t, line, t[:1] in QUOTES))
    return toks


def compare_tokens(old, new, lang):
    if lang == 'shell':
        la, lb = line_tokens(strip_shell(old)), line_tokens(strip_shell(new))
    else:
        la, lb = lex(old, lang), lex(new, lang)
    a = [t[0] for t in la]
    b = [t[0] for t in lb]
    if a == b:
        return 'identical', 0, []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    stderr_changes, problems = 0, []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if op == 'replace' and (i2 - i1) == (j2 - j1) and all(
                allowed_string_change(la[i1 + k], lb[j1 + k]) for k in range(i2 - i1)):
            stderr_changes += i2 - i1
            continue
        problems.append((op, a[i1:i2][:5], b[j1:j2][:5], (lb[j1][1] if j1 < len(lb) else '').strip()[:120]))
    if problems:
        return 'CODE DIFF', stderr_changes, problems
    return 'stderr/usage strings only', stderr_changes, []


# ---------------------------------------------------------------- python (AST)
class _DocStrip(ast.NodeTransformer):
    def _strip(self, node):
        self.generic_visit(node)
        body = getattr(node, 'body', None)
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
        return node

    visit_Module = visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _strip


def _stderr_context(stack):
    for node in stack:
        if isinstance(node, ast.Call):
            f = node.func
            name = ast.unparse(f) if hasattr(ast, 'unparse') else ''
            if name in ('sys.stderr.write', 'sys.exit', 'SystemExit') or name.endswith('.add_argument') \
                    or name.endswith('ArgumentParser'):
                return True
            if name == 'print' and any(k.arg == 'file' and 'stderr' in ast.unparse(k.value) for k in node.keywords):
                return True
        if isinstance(node, ast.Raise) and node.exc is not None and 'SystemExit' in ast.unparse(node.exc):
            return True
    return False


def _walk_compare(x, y, stack, out):
    if type(x) is not type(y):
        out.append(('node', stack))
        return
    if isinstance(x, ast.AST):
        stack = stack + [x]
        for field in x._fields:
            _walk_compare(getattr(x, field, None), getattr(y, field, None), stack, out)
    elif isinstance(x, list):
        if len(x) != len(y):
            out.append(('len', stack))
            return
        for p, q in zip(x, y):
            _walk_compare(p, q, stack, out)
    else:
        if x != y:
            node = stack[-1] if stack else None
            if isinstance(node, ast.Constant) and isinstance(x, str) and isinstance(y, str) and \
                    (_stderr_context(stack) or y.lower().startswith('usage:')):
                out.append(('stderr', stack))
            else:
                out.append(('value', stack))


def compare_python(old, new):
    try:
        ta, tb = ast.parse(old), ast.parse(new)
    except SyntaxError as e:
        return 'CODE DIFF', 0, [('syntax', str(e), '', '')]
    ta, tb = _DocStrip().visit(ta), _DocStrip().visit(tb)
    if ast.dump(ta) == ast.dump(tb):
        return 'identical', 0, []
    diffs = []
    _walk_compare(ta, tb, [], diffs)
    bad = [d for d in diffs if d[0] != 'stderr']
    if bad:
        probs = []
        for kind, stack in bad[:5]:
            node = stack[-1] if stack else None
            line = getattr(node, 'lineno', '?')
            probs.append((kind, type(node).__name__ if node else '', '', f'line {line}'))
        return 'CODE DIFF', len(diffs) - len(bad), probs
    return 'stderr/usage strings only', len(diffs), []


# ---------------------------------------------------------------- driver
def changed_files(base):
    out = git('diff', '--name-status', '-M', base, '--').decode('utf-8', 'replace')
    res = []
    for line in out.splitlines():
        cols = line.split('\t')
        st = cols[0]
        if st.startswith('R'):
            res.append((cols[1], cols[2]))
        elif st == 'M':
            res.append((cols[1], cols[1]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--base', default='main')
    ap.add_argument('--list', action='store_true', help='print every file, not only the summary')
    ap.add_argument('paths', nargs='*')
    a = ap.parse_args()
    root = git('rev-parse', '--show-toplevel').decode().strip()
    os.chdir(root)
    pairs = [(p, p) for p in a.paths] if a.paths else changed_files(a.base)
    pairs = [(o, n) for o, n in pairs if language(n) and (os.path.splitext(n)[1].lower() in CODE_EXT
                                                          or language(n) == 'docker')]
    counts = {'identical': 0, 'stderr/usage strings only': 0, 'CODE DIFF': 0}
    total_str = 0
    rows = []
    for old_path, new_path in pairs:
        old = git('show', f'{a.base}:{old_path}')
        if old is None or not os.path.isfile(new_path):
            continue
        old = old.decode('utf-8', 'replace').replace('\r\n', '\n')
        new = io.open(new_path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
        lang = language(new_path)
        if lang == 'python':
            status, nstr, probs = compare_python(old, new)
        else:
            status, nstr, probs = compare_tokens(old, new, lang)
        counts[status] += 1
        total_str += nstr
        rows.append((new_path, status, nstr, probs))
    print(f'Comment-only check against {a.base} (tools/verify_comment_only.py)')
    print(f'changed code files: {len(rows)} | identical after removing comments/docstrings: '
          f'{counts["identical"]} | stderr/usage strings only: {counts["stderr/usage strings only"]} '
          f'({total_str} strings) | CODE DIFF: {counts["CODE DIFF"]}')
    for path, status, nstr, probs in rows:
        if a.list or status != 'identical':
            extra = f' ({nstr} strings)' if nstr else ''
            print(f'  {status}{extra}: {path}')
            for p in probs:
                print(f'      {p}')
    return 1 if counts['CODE DIFF'] else 0


if __name__ == '__main__':
    sys.exit(main())
