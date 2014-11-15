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
			$ratingNumber = (int) $row['ranking'];
			$rating = "";
			$imdb_link = "http://www.imdb.com/title/tt" . $row["imdb"];

			for ($i = 0; $i < 10; $i++)
			{
				if ($i <= $ratingNumber)
					$rating .= '<img height="10" src="star.png" alt="" />';
				else
					$rating .= '<img height="10" src="starbad.png" alt="" />';
			}

			?>
			<div class="movie">
				<h3>Seeders: <?php echo $row['seeders']; ?></h3>
				<a href='<?php echo $imdb_link; ?>'>
				  <img class="affiche" src="<?php echo $row['picture']; ?>" />
				</a>
				<h4><?php echo $row['name']; ?></h4>
				<h5><?php echo $row['year']; ?></h5>
				<span><?php echo $rating . " (" . $ratingNumber . ")" ?></span>
				<h6><a href="<?php echo $row['magnet']; ?>">Launch (<?php echo $row['quality']; ?>)</a></h6>
			</div>
			<?php
		}

		?>
	</body>
</html>
