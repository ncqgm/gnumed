<?php
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html\


include ('connect.php');

pg_query ("begin work");
pg_query ("delete from substance_dosage where id_drug_dosage = $dosage_id");
pg_query ("delete from drug_dosage where id = $dosage_id");
pg_query ("commit");
?>

<html><body>
<h2>Deleted</h2>

<a href="viewdrugdosage.php?id=<?= $id ?>">Back</a>

</body></html>