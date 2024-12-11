	create table src_schema.CROP_PRODUCTION
	(
    State_Name NVARCHAR(100),       -- Name of the state
    District_Name NVARCHAR(100),    -- Name of the district
    Crop_Year INT,                  -- Year of crop production
    Season NVARCHAR(50),            -- Season of crop production
    Crop NVARCHAR(100),             -- Name of the crop
    Area FLOAT,                     -- Area under cultivation
    Production FLOAT                -- Crop production
);


select count(*) as total_records from src_schema.CROP_PRODUCTION