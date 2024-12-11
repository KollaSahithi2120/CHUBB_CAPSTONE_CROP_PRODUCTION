--Total Crop Production by Season, Crop, and Year
SELECT ds.season AS Season, c.crop AS Crop, y.crop_year AS Year, SUM(f.production) AS TotalProduction
FROM tgt.fact_crop_production f
JOIN tgt.dim_season ds ON f.dim_season_id = ds.dim_season_id  
JOIN tgt.dim_crop c ON f.dim_crop_id = c.dim_crop_id         
JOIN tgt.dim_date y ON f.crop_year = y.crop_year
WHERE y.crop_year BETWEEN 1997 AND 2015
GROUP BY ds.season, c.crop, y.crop_year
ORDER BY ds.season, y.crop_year;


-- Total Crop Production by Geography (State), Crop, and Year
SELECT g.state_name AS State, c.crop AS Crop, y.crop_year AS Year, SUM(f.production) AS TotalProduction
FROM tgt.fact_crop_production f
JOIN tgt.dim_crop c ON f.dim_crop_id = c.dim_crop_id
JOIN tgt.dim_date y ON f.crop_year = y.crop_year
JOIN tgt.dim_geography g ON f.dim_geography_id = g.dim_geography_id
WHERE y.crop_year BETWEEN 1997 AND 2015
GROUP BY g.state_name, c.crop, y.crop_year
ORDER BY g.state_name, y.crop_year;

--Crop Production by Season and Year (Total per Season)
SELECT ds.season AS Season, y.crop_year AS Year, SUM(f.production) AS TotalProduction
FROM tgt.fact_crop_production f
JOIN tgt.dim_season ds ON f.dim_season_id = ds.dim_season_id
JOIN tgt.dim_date y ON f.crop_year = y.crop_year
WHERE y.crop_year BETWEEN 1997 AND 2015
GROUP BY ds.season, y.crop_year
ORDER BY ds.season, y.crop_year;

--Crop Production by District (Geography) and Crop
SELECT g.district_name AS District, c.crop AS Crop, SUM(f.production) AS TotalProduction
FROM tgt.fact_crop_production f
JOIN tgt.dim_crop c ON f.dim_crop_id = c.dim_crop_id
JOIN tgt.dim_geography g ON f.dim_geography_id = g.dim_geography_id
GROUP BY g.district_name, c.crop
ORDER BY g.district_name, c.crop;

--Crop Area and Production Summary by Season, Crop, and Year
SELECT ds.season AS Season, c.crop AS Crop, y.crop_year AS Year, 
       SUM(f.area) AS TotalArea, SUM(f.production) AS TotalProduction
FROM tgt.fact_crop_production f
JOIN tgt.dim_season ds ON f.dim_season_id = ds.dim_season_id
JOIN tgt.dim_crop c ON f.dim_crop_id = c.dim_crop_id
JOIN tgt.dim_date y ON f.crop_year = y.crop_year
WHERE y.crop_year BETWEEN 1997 AND 2015
GROUP BY ds.season, c.crop, y.crop_year
ORDER BY ds.season, y.crop_year;



