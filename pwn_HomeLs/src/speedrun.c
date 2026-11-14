#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>

#define BSS_CMD_LEN  18 // Quanto è lungo il comando in BSS
#define USERNAME_LEN 82 // Quanto è lungo lo username massimo consentito

char bss_str[BSS_CMD_LEN]; // Teniamo questo spazio in BSS

void print_banner() {
    puts(
        "\n"
        "\n"
        "█   █                   ▀█▀       \n"
        "█▄▄▄█ ▄▀▀▀▄ █▀▄▀▄ ▄▀▀▀▄  █    ▄▀▀▀ \n"
        "█   █ █   █ █ █ █ █▀▀▀▀  █  ▄  ▀▀▄ \n"
        "▀   ▀  ▀▀▀  ▀ ▀ ▀  ▀▀▀  ▀▀▀▀▀ ▀▀▀  \n"
    );
}

void setup() { // Disabilita buffering
        setvbuf(stdin , NULL, _IONBF, 0);
        setvbuf(stdout, NULL, _IONBF, 0);
        setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
        setup();
        print_banner();
        
        // Carichiamo il comando in BSS
        snprintf(bss_str, BSS_CMD_LEN, "/bin/ls -l /home/"); // su mac è /Users/
        
        // Chiediamo lo username
        char user[USERNAME_LEN] = {0};
        puts("What's your username?:");
        read(STDIN_FILENO, user, USERNAME_LEN); // oppure fgets (oppure forse anche sscanf)
        
        // command injection prevention (hopefully)
        if (strpbrk(user, ";|(!)&\\*`") != NULL){
                printf("I don't like injections XD");
                return 1;
        }
        
        // Stampa lo username in verde
        printf("\nListing the directory contents of: \033[92m");
        printf(user); // <- FORMAT STRING VULN (%n)
        printf("\033[0m"); // Terminatore Green

        char shell_command[BSS_CMD_LEN + USERNAME_LEN] = {0}; // buffer del comando completo
        strcpy(shell_command, bss_str); // Riempio il primo pezzo
        strcat(shell_command, user);    // Concateno il secondo pezzo
        system(strtok(shell_command, "\n")); // prendi solo la prima riga
        return 0;
}