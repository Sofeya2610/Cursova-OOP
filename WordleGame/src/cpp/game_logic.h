#ifndef GAME_LOGIC_H
#define GAME_LOGIC_H

#include <string>
#include <vector>

extern const int WORD_LENGTH;

// глобальні змінні
extern std::string TARGET_WORD;
extern bool HINT_USED;
extern std::string CURRENT_MODE; // EASY або HARD

// завантаження словника
std::vector<std::string> load_dictionary(const std::string &filename);

// словник для поточного режиму
std::vector<std::string> load_dictionary_for_mode(const std::string &mode);

// генерація фідбеку Wordle-стилю
std::string generate_feedback(const std::string &guess, const std::string &target);

// підказка: повертає "index letter" або "-1 -"
std::string get_hint();

#endif // GAME_LOGIC_H
