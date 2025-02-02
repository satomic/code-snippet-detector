import re
import json

class CodePreprocessor:

    def process(self, code_block: dict, var_replace=True) -> dict:
        """归一化处理代码块"""
        file_path = code_block["file"]
        extension = file_path.split('.')[-1]

        language_keywords = {
            'py': set([
                'self', 'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
            ]),
            'java': set([
                'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'null', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while'
            ]),
            'cpp': set([
                'alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel', 'atomic_commit', 'atomic_noexcept', 'auto', 'bitand', 'bitor', 'bool', 'break', 'case', 'catch', 'char', 'char8_t', 'char16_t', 'char32_t', 'class', 'compl', 'concept', 'const', 'consteval', 'constexpr', 'constinit', 'const_cast', 'continue', 'co_await', 'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected', 'public', 'reflexpr', 'register', 'reinterpret_cast', 'requires', 'return', 'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast', 'struct', 'switch', 'synchronized', 'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq'
            ]),
            'cs': set([
                'abstract', 'as', 'base', 'bool', 'break', 'byte', 'case', 'catch', 'char', 'checked', 'class', 'const', 'continue', 'decimal', 'default', 'delegate', 'do', 'double', 'else', 'enum', 'event', 'explicit', 'extern', 'false', 'finally', 'fixed', 'float', 'for', 'foreach', 'goto', 'if', 'implicit', 'in', 'int', 'interface', 'internal', 'is', 'lock', 'long', 'namespace', 'new', 'null', 'object', 'operator', 'out', 'override', 'params', 'private', 'protected', 'public', 'readonly', 'ref', 'return', 'sbyte', 'sealed', 'short', 'sizeof', 'stackalloc', 'static', 'string', 'struct', 'switch', 'this', 'throw', 'true', 'try', 'typeof', 'uint', 'ulong', 'unchecked', 'unsafe', 'ushort', 'using', 'virtual', 'void', 'volatile', 'while'
            ]),
            'js': set([
                'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do', 'else', 'enum', 'export', 'extends', 'false', 'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new', 'null', 'return', 'super', 'switch', 'this', 'throw', 'true', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield'
            ]),
            'go': set([
                'break', 'case', 'chan', 'const', 'continue', 'default', 'defer', 'else', 'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import', 'interface', 'map', 'package', 'range', 'return', 'select', 'struct', 'switch', 'type', 'var'
            ]),
            'php': set([
                'abstract', 'and', 'array', 'as', 'break', 'callable', 'case', 'catch', 'class', 'clone', 'const', 'continue', 'declare', 'default', 'do', 'echo', 'else', 'elseif', 'empty', 'enddeclare', 'endfor', 'endforeach', 'endif', 'endswitch', 'endwhile', 'eval', 'exit', 'extends', 'final', 'finally', 'fn', 'for', 'foreach', 'function', 'global', 'goto', 'if', 'implements', 'include', 'include_once', 'instanceof', 'insteadof', 'interface', 'isset', 'list', 'match', 'namespace', 'new', 'or', 'print', 'private', 'protected', 'public', 'require', 'require_once', 'return', 'static', 'switch', 'throw', 'trait', 'try', 'unset', 'use', 'var', 'while', 'xor', 'yield'
            ])
        }

        language_builtin_modules = {
            'py': set([
            'os', 'sys', 'json', 're', 'asyncio', 'datetime', 'pathlib', 'logging', 'time', 'random',
            'subprocess', 'typing', 'multiprocessing', 'functools', 'itertools', 'collections', 'math',
            'statistics', 'decimal', 'fractions', 'argparse', 'configparser', 'enum', 'inspect', 'io',
            'csv', 'sqlite3', 'pickle', 'queue', 'threading', 'http', 'ftplib', 'socket', 'urllib',
            'xml', 'xml.etree.ElementTree', 'html', 'html.parser', 'gzip', 'bz2', 'lzma', 'base64',
            'hashlib', 'hmac', 'logging.config', 'logging.handlers', 'email', 'abc',
            'concurrent.futures', 'glob', 'print'
            ]),
            'java': set([
            'java.util', 'java.io', 'java.net', 'java.nio', 'java.lang', 'javax.swing', 'javax.servlet',
            'java.math', 'java.sql', 'java.text', 'java.time', 'java.security', 'java.awt', 'java.beans',
            'java.rmi', 'javax.xml', 'javax.xml.parsers', 'javax.xml.stream', 'javax.xml.transform',
            'javax.xml.xpath', 'javax.naming', 'javax.net', 'javax.net.ssl', 'java.applet',
            'java.awt.color', 'java.awt.font', 'java.awt.geom', 'java.awt.image',
            'java.util.concurrent', 'java.util.concurrent.atomic', 'java.util.concurrent.locks',
            'java.util.logging', 'java.util.jar', 'java.util.zip', 'java.util.regex',
            'java.security.acl', 'java.security.cert', 'java.security.interfaces', 'java.security.spec',
            'java.text.spi', 'java.time.chrono', 'java.time.format', 'java.time.temporal',
            'java.time.zone', 'java.sql.DriverManager', 'java.sql.Connection', 'java.sql.Statement',
            'java.sql.ResultSet', 'javax.crypto'
            ]),
            'cpp': set([
            'algorithm', 'array', 'atomic', 'bitset', 'chrono', 'codecvt', 'complex',
            'condition_variable', 'deque', 'exception', 'fstream', 'functional', 'initializer_list',
            'iomanip', 'ios', 'iosfwd', 'iostream', 'istream', 'iterator', 'limits', 'list', 'locale',
            'map', 'memory', 'mutex', 'new', 'numeric', 'optional', 'ostream', 'queue', 'random', 'regex',
            'scoped_allocator', 'set', 'shared_mutex', 'sstream', 'stack', 'stdexcept', 'streambuf',
            'string', 'strstream', 'system_error', 'thread', 'tuple', 'type_traits', 'typeindex',
            'typeinfo', 'unordered_map', 'unordered_set', 'utility', 'valarray', 'vector'
            ]),
            'cs': set([
            'System', 'System.Collections', 'System.Collections.Generic', 'System.Collections.Concurrent',
            'System.Configuration', 'System.ComponentModel', 'System.Data', 'System.Data.SqlClient',
            'System.Diagnostics', 'System.Globalization', 'System.IO', 'System.IO.Compression',
            'System.IO.FileSystem', 'System.Linq', 'System.Linq.Expressions', 'System.Net', 'System.Net.Http',
            'System.Net.Sockets', 'System.Net.Security', 'System.Reflection', 'System.Resources',
            'System.Runtime', 'System.Runtime.Serialization', 'System.Runtime.InteropServices',
            'System.Security', 'System.Security.Cryptography', 'System.ServiceModel', 'System.ServiceProcess',
            'System.Text', 'System.Text.RegularExpressions', 'System.Threading', 'System.Threading.Tasks',
            'System.Timers', 'System.Transactions', 'System.Web', 'System.Web.Http', 'System.Web.Mvc',
            'System.Web.Razor', 'System.Web.Routing', 'System.Windows', 'System.Windows.Forms',
            'Microsoft.CSharp', 'Microsoft.VisualBasic', 'System.Xml', 'System.Xml.Linq',
            'System.Xml.Serialization', 'System.Deployment', 'System.Design', 'System.Drawing',
            'System.Drawing.Design', 'System.EnterpriseServices'
            ]),
            'js': set([
            'fs', 'http', 'https', 'path', 'assert', 'buffer', 'child_process', 'cluster', 'console',
            'crypto', 'dgram', 'dns', 'domain', 'events', 'net', 'os', 'process', 'punycode',
            'querystring', 'readline', 'repl', 'stream', 'string_decoder', 'timers', 'tty', 'url',
            'util', 'zlib', 'v8', 'vm', 'worker_threads', 'perf_hooks', 'async_hooks', 'http2', 'node:test',
            'express', 'sequelize', 'mocha', 'chai', 'jsonwebtoken', 'mongoose', 'debug', 'cors',
            'body-parser', 'escape-html', 'node-fetch', 'axios'
            ]),
            'go': set([
            'fmt', 'os', 'net', 'http', 'time', 'strings', 'io', 'bufio', 'sync', 'sync/atomic', 'reflect',
            'bytes', 'encoding', 'encoding/json', 'encoding/xml', 'unicode', 'unicode/utf8', 'io/ioutil',
            'strconv', 'math', 'math/rand', 'path', 'path/filepath', 'regexp', 'runtime', 'runtime/debug',
            'runtime/trace', 'sort', 'context', 'flag', 'log', 'log/syslog', 'database/sql',
            'compress/gzip', 'compress/zlib', 'crypto', 'crypto/aes', 'crypto/cipher', 'crypto/des',
            'crypto/dsa', 'crypto/ecdsa', 'crypto/elliptic', 'crypto/hmac', 'crypto/md5', 'crypto/rand',
            'crypto/rc4', 'crypto/rsa', 'crypto/sha256', 'crypto/tls', 'crypto/x509', 'hash', 'hash/crc32'
            ]),
            'php': set([
            'array', 'string', 'json', 'mysqli', 'PDO', 'Exception', 'CurlHandle', 'DateTime', 'DOMDocument',
            'SimpleXMLElement', 'PDOStatement', 'Error', 'SplFileObject', 'SplDoublyLinkedList', 'SplStack',
            'SplQueue', 'ReflectionClass', 'ReflectionMethod', 'ReflectionProperty', 'ReflectionFunction',
            'stream_wrapper_register', 'openssl', 'ctype', 'filter', 'hash', 'iconv', 'mbstring', 'pcre',
            'session', 'pdo_mysql', 'soap', 'sockets', 'spl', 'standard', 'zlib', 'bcmath', 'calendar',
            'dba', 'ftp', 'gd', 'intl', 'ldap', 'phar', 'readline', 'shmop', 'sysvmsg', 'sysvsem',
            'sysvshm'
            ])
        }

        code = code_block["code"]
        keywords = language_keywords.get(extension, set())
        builtin_modules = language_builtin_modules.get(extension, set())

        # 删除注释
        if extension == 'py':
            code = re.sub(r'#.*', '', code)
            code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
            code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        elif extension in ['java', 'js', 'cpp', 'cs']:
            code = re.sub(r'//.*|/\*[\s\S]*?\*/', '', code)
        elif extension == 'go':
            code = re.sub(r'//.*|/\*[\s\S]*?\*/', '', code)
        elif extension == 'php':
            code = re.sub(r'//.*|#.*|/\*[\s\S]*?\*/', '', code)

        # 合并空白字符
        code = re.sub(r'\s+', ' ', code)

        # 替换变量名
        def replace_var(match):
            var_name = match.group(0)
            if var_name in keywords or var_name in builtin_modules:
                return var_name
            return 'VAR'

        if var_replace:
            code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', replace_var, code)
        
        return {
            **code_block,
            "normalized_code": code.strip()
        }


if __name__ == "__main__":
    preprocessor = CodePreprocessor()
    code_block = {
        "type": "function",
        "name": "__init__",
        "code": """
        def __init__(self):
            self.loop = asyncio.get_event_loop()
            self.usernames = {}
            self.usernames_file_path = os.path.join(log_file_path, "proxy_auth_cache.json")
            self.usage_file_path = os.path.join(log_file_path, "usage")
            self.metrics_file_path = os.path.join(log_file_path, "metrics")
            self.current_date = datetime.utcnow().date()
            self.load_usernames()
            ctx.log.info("✅ Initialized ProxyReqRspSaveToJson plugin")
        """,
        "file": "tmp/example.py"
    }
    processed_block = preprocessor.process(code_block)
    print(json.dumps(processed_block, indent=2))