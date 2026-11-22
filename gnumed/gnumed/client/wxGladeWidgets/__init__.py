# Copyright: Karsten Hilbert
# GPL-2.0-or-later (details at https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)
# add support for local_code overrides:
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
__path__.reverse()
