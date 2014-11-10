<!DOCTYPE html>
<html>
	<head>
		<title>Movie list</title>
		<link rel="stylesheet" type="text/css" href="style.css" />
	</head>
	<body>
		<?php

		$db = new PDO("../db/database.sqlite");
		$result = $pdo->query("SELECT * FROM movie ORDER BY seed DESC LIMIT 1000");

		foreach ($result as $row)
		{
			?>
			<div class="movie">
				<img src="<?php echo $row['picture']; ?>" />
				<h4><?php echo $row['name']; ?></h4>
				<h5><a href="<?php echo $row['magnet']; ?>">Télécharger</a></h5>
			</div>
			<?php
		}

		?>
	</body>
</html>