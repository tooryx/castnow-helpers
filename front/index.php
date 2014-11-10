<!DOCTYPE html>
<html>
	<head>
		<title>Movie list</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<link rel="stylesheet" type="text/css" href="style.css" />
	</head>
	<body>
		<?php

		$db = new PDO("sqlite:/var/www/html/castnow/db/database.sqlite");
		$result = $db->query("SELECT * FROM movie ORDER BY seeders DESC");

		foreach ($result as $row)
		{
			?>
			<div class="movie">
				<img src="<?php echo $row['picture']; ?>" />
				<h4><?php echo $row['name']; ?></h4>
				<h5><?php echo $row['year']; ?></h5>
				<h6><a href="<?php echo $row['magnet']; ?>">Regarder (<?php echo $row['quality']; ?>)</a></h6>
			</div>
			<?php
		}

		?>
	</body>
</html>