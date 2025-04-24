-- Création de la table des planètes
CREATE TABLE planets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(50) NOT NULL,
  distance FLOAT NOT NULL,
  temperature FLOAT NOT NULL,
  habitable BOOLEAN DEFAULT 0,
  description TEXT,
  image_url VARCHAR(255),
  discovery_date DATE
);

-- Création de la table des explorateurs
CREATE TABLE explorers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  speciality VARCHAR(100) NOT NULL,
  experience INT DEFAULT 0,
  email VARCHAR(255) NOT NULL
);

-- Création de la table des missions
CREATE TABLE missions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  planet_id INT NOT NULL,
  explorer_id INT NOT NULL,
  departure_date DATE NOT NULL,
  duration INT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  FOREIGN KEY (planet_id) REFERENCES planets(id),
  FOREIGN KEY (explorer_id) REFERENCES explorers(id)
);

-- Insertion de données de test
INSERT INTO planets (name, type, distance, temperature, habitable, description, discovery_date)
VALUES 
('Xandros', 'rocheuse', 87.3, 400, 0, 'Planète volcanique', '2150-04-01'),
('Gaïa-2', 'habitable', 45.7, 23.5, 1, 'Similaire à la Terre', '2150-04-02'),
('Jupiter', 'rocheuse', 50.6, 25.0, 0, 'Elle est de couleur orange', 'jupiter_4x3.avif', '1994-06-08');

