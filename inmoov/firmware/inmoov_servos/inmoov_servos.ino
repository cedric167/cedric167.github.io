// Firmware InMoov : reçoit les ordres de l'ordinateur portable par USB et
// pilote jusqu'à 32 servos via deux cartes PCA9685 (adresses 0x40 et 0x41).
//
// Carte : Arduino Mega 2560 (un Uno suffit aussi : seul le bus I2C est utilisé).
// Bibliothèque : "Adafruit PWM Servo Driver Library" (gestionnaire de bibliothèques).
//
// Protocole série (115200 bauds, une commande par ligne) :
//   P                      -> ping, répond OK (ou ESTOP)
//   S <canal> <angle> <v>  -> amène le servo <canal> (0-31) à <angle> (0-180)
//                             à <v> degrés par seconde ; répond OK
//   R                      -> relâche tous les servos (plus de signal) ; répond OK
// Si le bouton d'arrêt d'urgence est enfoncé, toute commande répond ESTOP
// et plus aucun servo ne bouge.

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

const int NB_SERVOS = 32;
const int BROCHE_ARRET_URGENCE = 2;   // contact du bouton d'arrêt (fermé = normal, ouvert = arrêt)
const int IMPULSION_MIN_US = 500;     // impulsion à 0°   (à ajuster selon tes servos)
const int IMPULSION_MAX_US = 2500;    // impulsion à 180°
const unsigned long PERIODE_MS = 20;  // un pas de lissage toutes les 20 ms

Adafruit_PWMServoDriver cartes[2] = {Adafruit_PWMServoDriver(0x40), Adafruit_PWMServoDriver(0x41)};

float position[NB_SERVOS];
float cible[NB_SERVOS];
float vitesse[NB_SERVOS];   // degrés par seconde
bool actif[NB_SERVOS];      // false tant que le servo n'a reçu aucun ordre
unsigned long dernierPas = 0;
char ligne[32];
int longueur = 0;

bool arretUrgence() {
  // Le bouton relie la broche à la masse en temps normal : s'il est enfoncé
  // ou si un fil est coupé, la broche remonte à HIGH et on s'arrête.
  return digitalRead(BROCHE_ARRET_URGENCE) == HIGH;
}

void envoyerAngle(int canal, float angle) {
  long us = IMPULSION_MIN_US + (long)(angle * (IMPULSION_MAX_US - IMPULSION_MIN_US) / 180.0);
  int ticks = (int)(us * 4096L / 20000L);  // 50 Hz = 20 000 µs par période
  cartes[canal / 16].setPWM(canal % 16, 0, ticks);
}

void relacherTout() {
  for (int c = 0; c < NB_SERVOS; c++) {
    cartes[c / 16].setPWM(c % 16, 0, 0);
    actif[c] = false;
  }
}

void traiter(char *commande) {
  if (arretUrgence()) {
    Serial.println("ESTOP");
    return;
  }
  if (commande[0] == 'P') {
    Serial.println("OK");
  } else if (commande[0] == 'R') {
    relacherTout();
    Serial.println("OK");
  } else if (commande[0] == 'S') {
    int canal, angle, v;
    if (sscanf(commande + 1, "%d %d %d", &canal, &angle, &v) != 3 || canal < 0 || canal >= NB_SERVOS) {
      Serial.println("ERR commande");
      return;
    }
    cible[canal] = constrain(angle, 0, 180);
    vitesse[canal] = constrain(v, 5, 300);
    if (!actif[canal]) {
      // Premier ordre : on ne connaît pas la position réelle, on y va directement
      // (le programme Python commence toujours par la position de repos, lentement).
      position[canal] = cible[canal];
      envoyerAngle(canal, position[canal]);
      actif[canal] = true;
    }
    Serial.println("OK");
  } else {
    Serial.println("ERR inconnue");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BROCHE_ARRET_URGENCE, INPUT_PULLUP);
  for (int i = 0; i < 2; i++) {
    cartes[i].begin();
    cartes[i].setOscillatorFrequency(25000000);
    cartes[i].setPWMFreq(50);
  }
  for (int c = 0; c < NB_SERVOS; c++) {
    position[c] = cible[c] = 90;
    vitesse[c] = 60;
    actif[c] = false;
  }
  relacherTout();
}

void loop() {
  while (Serial.available()) {
    char caractere = Serial.read();
    if (caractere == '\n' || caractere == '\r') {
      if (longueur > 0) {
        ligne[longueur] = '\0';
        traiter(ligne);
        longueur = 0;
      }
    } else if (longueur < (int)sizeof(ligne) - 1) {
      ligne[longueur++] = caractere;
    }
  }

  unsigned long maintenant = millis();
  if (maintenant - dernierPas < PERIODE_MS) return;
  dernierPas = maintenant;
  if (arretUrgence()) return;  // on fige tout : plus aucun pas de mouvement

  // Lissage : chaque servo avance vers sa cible d'au plus vitesse × 20 ms.
  for (int c = 0; c < NB_SERVOS; c++) {
    if (!actif[c] || position[c] == cible[c]) continue;
    float pas = vitesse[c] * PERIODE_MS / 1000.0;
    float ecart = cible[c] - position[c];
    position[c] = abs(ecart) <= pas ? cible[c] : position[c] + (ecart > 0 ? pas : -pas);
    envoyerAngle(c, position[c]);
  }
}
