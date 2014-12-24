APPNAME = 'MRSG'
VERSION = '1.0.0'

top = '.'
out = 'build'

def options(ctx):
    ctx.add_option('--search-path', action='store', default='', help='Search paths')
    ctx.load('compiler_c')

def configure(ctx):
    search_paths = []
    if len(ctx.options.search_path) > 0:
        search_paths = ctx.options.search_path.split(':')
        ctx.env.append_value('INCLUDES', [ s + '/include' for s in search_paths])
        ctx.env.append_value('LIBPATH', [ s + '/lib'     for s in search_paths])
    ctx.load('compiler_c')
    ctx.check_cc(lib = 'm')
    ctx.check_cc(lib = 'simgrid')
    ctx.check_cc(header_name = 'msg/msg.h')

def build(ctx):
    ctx.shlib(
        source=ctx.path.ant_glob('src/*.c'),
        includes=['include'],
        target='mrsg',
        install_path='${LIBDIR}',
        use='SIMGRID')

    ctx.install_files('${PREFIX}/include', [
        'include/mrsg.h',
        'include/common.h',
        'include/scheduling.h'])
